import os
import json
import logging
import numpy as np
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import FloatType
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import Tokenizer, StopWordsRemover, NGram, SQLTransformer, HashingTF, IDF
from pyspark.ml.classification import LinearSVC, LinearSVCModel
from sklearn.metrics import f1_score, confusion_matrix, classification_report, accuracy_score

URL_S3_SILVER = os.environ.get("URL_S3_SILVER", "s3a://amazon-reviews-datalake/silver")
MODEL_SAVE_PATH = os.environ.get("MODEL_SAVE", "s3a://amazon-reviews-datalake/silver/model")
BINARY_MODEL_PATH = f"{MODEL_SAVE_PATH}/sentiment_binary_lsvm/class_weighting"
MARGIN_SAVE_PATH = f"{MODEL_SAVE_PATH}/sentiment_margin_lsvm"

CATEGORIES = ["All_Beauty", "Amazon_Fashion"]

def build_binary_lsvm_pipeline(num_features: int = 2**19) -> Pipeline:
    """
    Build PySpark ML Binary Pipeline with Stopword-Pruned N-grams (Negation Preserved):
    Tokenizer -> StopWordsRemover -> NGram(n=2) -> SQLTransformer (concat) ->
    HashingTF (num_features=524,288) -> IDF -> LinearSVC (native binary classifier)
    """
    tokenizer = Tokenizer(inputCol="review_text", outputCol="raw_words")
    
    default_stops = StopWordsRemover.loadDefaultStopWords("english")
    negation_words = {"not", "no", "never", "nor", "neither", "barely", "hardly", "scarcely", "rarely", "seldom", "despite"}
    custom_stops = [w for w in default_stops if w not in negation_words]
    
    stop_remover = StopWordsRemover(
        inputCol="raw_words",
        outputCol="unigrams",
        stopWords=custom_stops
    )
    ngram = NGram(n=2, inputCol="unigrams", outputCol="bigrams")
    sql_transformer = SQLTransformer(
        statement="SELECT *, concat(unigrams, bigrams) AS words FROM __THIS__"
    )
    hashingTF = HashingTF(
        inputCol="words",
        outputCol="rawFeatures",
        numFeatures=num_features
    )
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    
    lsvc = LinearSVC(
        featuresCol="features",
        labelCol="label",
        weightCol="class_weight",
        maxIter=15,
        regParam=0.1
    )
    
    pipeline = Pipeline(stages=[tokenizer, stop_remover, ngram, sql_transformer, hashingTF, idf, lsvc])
    return pipeline

def evaluate_3class_predictions(y_true, y_pred, split_name: str, logger: logging.Logger):
    """Evaluate and log 3-class classification metrics."""
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro")
    weighted_f1 = f1_score(y_true, y_pred, average="weighted")
    report = classification_report(
        y_true,
        y_pred,
        target_names=["Negative (0)", "Uncertain (1)", "Positive (2)"],
        digits=4
    )
    cm = confusion_matrix(y_true, y_pred)

    logger.info("==================================================")
    logger.info(f"[{split_name}] Accuracy    : {acc:.4f}")
    logger.info(f"[{split_name}] Weighted F1 : {weighted_f1:.4f}")
    logger.info(f"[{split_name}] Macro-F1    : {macro_f1:.4f}")
    logger.info(f"[{split_name}] Classification Report:\n{report}")
    logger.info(f"[{split_name}] Confusion Matrix:\n{cm}")
    logger.info("==================================================")
    return acc, macro_f1, weighted_f1

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("Margin_LinearSVM_Approach_C")

    try:
        spark = (
            SparkSession.builder.appName("Sentiment_Margin_LinearSVM_Tuning_Combined")
            .master(os.environ.get("SPARK_MASTER_URL", "spark://spark-master:7077"))
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            .config("spark.hadoop.fs.s3a.access.key", os.environ.get("ACCESS_KEY"))
            .config("spark.hadoop.fs.s3a.secret.key", os.environ.get("SECRET_KEY"))
            .config("spark.hadoop.fs.s3a.endpoint", os.environ.get("MINIO_ENDPOINT", "http://minio:9000"))
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .config("spark.executor.memory", "3g")
            .config("spark.driver.memory", "2g")
            .config("spark.driver.maxResultSize", "2g")
            .config("spark.memory.fraction", "0.8")
            .getOrCreate()
        )
        logger.info("Spark Session created successfully.")

        # 1. Load or train the Binary Linear SVM PipelineModel
        try:
            logger.info(f"Attempting to load trained Binary Linear SVM model from: {BINARY_MODEL_PATH}")
            binary_model = PipelineModel.load(BINARY_MODEL_PATH)
            logger.info("Successfully loaded existing Binary Linear SVM model.")
        except Exception as load_err:
            logger.warning(f"Could not load pre-trained binary model ({str(load_err)}). Training a fresh binary model...")
            train_path = f"{URL_S3_SILVER}/sentiment_splits/*/train"
            raw_train_df = spark.read.parquet(train_path)
            train_df = (
                raw_train_df.filter(F.col("label").isin([0.0, 2.0]))
                .withColumn("label", F.when(F.col("label") == 2.0, 1.0).otherwise(0.0))
            )
            train_count = train_df.count()
            class_counts = train_df.groupBy("label").count().collect()
            num_classes = len(class_counts)
            weight_dict = {row["label"]: train_count / (num_classes * row["count"]) for row in class_counts}
            mapping_expr = F.create_map([F.lit(x) for pair in weight_dict.items() for x in pair])
            train_df_weighted = train_df.withColumn("class_weight", mapping_expr[F.col("label")])
            
            pipeline = build_binary_lsvm_pipeline(num_features=2**19)
            binary_model = pipeline.fit(train_df_weighted)
            binary_model.write().overwrite().save(BINARY_MODEL_PATH)
            logger.info(f"Fresh binary model trained and saved to: {BINARY_MODEL_PATH}")

        # 2. Read full Validation set containing ALL 3 classes (Negative: 0.0, Neutral: 1.0, Positive: 2.0)
        val_path = f"{URL_S3_SILVER}/sentiment_splits/*/val"
        logger.info(f"Reading full 3-class Validation data from: {val_path}")
        val_df = spark.read.parquet(val_path)
        val_count = val_df.count()
        logger.info(f"Total Validation rows: {val_count:,}")

        # 3. Generate rawPrediction with binary model
        logger.info("Generating raw signed margin distances on Validation set...")
        predictions = binary_model.transform(val_df)

        # In PySpark LinearSVC, rawPrediction is a Vector [-margin, margin].
        # margin = rawPrediction[1] is the signed distance to the separating hyperplane.
        extract_margin_udf = F.udf(lambda v: float(v[1]), FloatType())
        pred_df = predictions.withColumn("margin", extract_margin_udf(F.col("rawPrediction")))

        logger.info("Collecting labels and margins for threshold optimization...")
        val_pd = pred_df.select("label", "margin", "category").toPandas()

        y_true = val_pd["label"].values.astype(float)
        margins = val_pd["margin"].values.astype(float)

        # 4. Convert Margin to Sigmoid Probability and Prediction Confidence
        # In Linear SVM:
        #   margin = signed distance to decision boundary f(x) = w^T x + b
        #   P(Positive) = 1 / (1 + exp(-margin))  via Platt scaling (Sigmoid)
        #   Confidence = max(P, 1 - P) in [0.5, 1.0]
        # Relationship between Margin threshold (theta) and Probability band:
        #   theta = 0.40 <=> P in [0.401, 0.599] <=> Confidence <= 59.87%
        #   theta = 0.50 <=> P in [0.378, 0.622] <=> Confidence <= 62.25%
        #   theta = 0.60 <=> P in [0.354, 0.646] <=> Confidence <= 64.57%
        prob_pos = 1.0 / (1.0 + np.exp(-margins))
        confidence = np.maximum(prob_pos, 1.0 - prob_pos)

        logger.info("Computing threshold scan across margin range [0.05, 2.00]...")
        candidate_thetas = np.arange(0.05, 2.05, 0.05)
        best_theta = 0.0
        best_macro_f1 = -1.0
        best_acc = 0.0

        tuning_history = []
        for theta in candidate_thetas:
            y_pred = np.where(margins > theta, 2.0, np.where(margins < -theta, 0.0, 1.0))
            macro = f1_score(y_true, y_pred, average="macro")
            acc = accuracy_score(y_true, y_pred)
            f1_neu = f1_score(y_true == 1.0, y_pred == 1.0)

            # Corresponding probability band
            p_upper = 1.0 / (1.0 + np.exp(-theta))
            conf_level = p_upper

            tuning_history.append({
                "theta": round(float(theta), 2),
                "conf_thresh": round(float(conf_level * 100), 2),
                "macro_f1": round(float(macro), 4),
                "acc": round(float(acc), 4),
                "f1_neutral": round(float(f1_neu), 4)
            })
            if macro > best_macro_f1:
                best_macro_f1 = macro
                best_theta = theta
                best_acc = acc

        logger.info("==================================================")
        logger.info(f">>> GLOBAL OPTIMAL THRESHOLD FOUND: theta* = {best_theta:.2f} <<<")
        logger.info(f">>> Peak Validation Macro-F1: {best_macro_f1:.4f} | Accuracy: {best_acc:.4f} <<<")
        logger.info("==================================================")

        # 5. Targeted evaluation for specific thresholds requested: theta = 0.40, 0.50, and best_theta
        target_thetas = [0.40, 0.50]
        if round(float(best_theta), 2) not in target_thetas:
            target_thetas.append(round(float(best_theta), 2))
        target_thetas = sorted(target_thetas)

        for target_th in target_thetas:
            p_low = 1.0 / (1.0 + np.exp(target_th))
            p_high = 1.0 / (1.0 + np.exp(-target_th))
            conf_cap = p_high * 100.0

            logger.info("**************************************************")
            logger.info(f"EVALUATION AT THRESHOLD: theta = {target_th:.2f}")
            logger.info(f"  Mapping Rule:")
            logger.info(f"    - Positive (2.0): margin >  {target_th:.2f}  (P(pos) > {p_high:.4f} or Confidence > {conf_cap:.2f}%)")
            logger.info(f"    - Negative (0.0): margin < -{target_th:.2f}  (P(pos) < {p_low:.4f}  or Confidence > {conf_cap:.2f}%)")
            logger.info(f"    - Neutral  (1.0): |margin| <= {target_th:.2f} (P(pos) in [{p_low:.4f}, {p_high:.4f}] or Confidence <= {conf_cap:.2f}%)")
            logger.info("**************************************************")

            curr_y_pred = np.where(margins > target_th, 2.0, np.where(margins < -target_th, 0.0, 1.0))
            evaluate_3class_predictions(y_true, curr_y_pred, f"OVERALL_COMBINED_VAL (theta={target_th:.2f}, conf<={conf_cap:.1f}%)", logger)

            # Per-category evaluation
            for cat in CATEGORIES:
                cat_mask = (val_pd["category"] == cat).values
                cat_y_true = y_true[cat_mask]
                cat_y_pred = curr_y_pred[cat_mask]
                evaluate_3class_predictions(cat_y_true, cat_y_pred, f"CATEGORY_{cat}_VAL (theta={target_th:.2f})", logger)

        # 6. Save metadata configuration for downstream batch inference
        config = {
            "method": "Binary_LinearSVM_Margin_Confidence",
            "chosen_theta": 0.30,
            "optimal_theta": round(float(best_theta), 4),
            "confidence_threshold": 57.44,
            "classes": ["Negative", "Uncertain", "Positive"],
            "binary_model_path": BINARY_MODEL_PATH,
            "validation_macro_f1": round(float(best_macro_f1), 4),
            "validation_accuracy": round(float(best_acc), 4)
        }
        
        config_path = f"{MARGIN_SAVE_PATH}/margin_config.json"
        config_df = spark.createDataFrame([config])
        config_df.write.mode("overwrite").json(config_path)
        logger.info(f"Approach C configuration saved successfully to: {config_path}")

    except Exception as e:
        logger.error(f"Error occurred during Approach C tuning: {str(e)}", exc_info=True)
        raise
    finally:
        if "spark" in locals():
            spark.stop()
            logger.info("Spark Session stopped.")

# Execution Command:
# docker exec -it spark-master spark-submit --driver-memory 2g --executor-memory 3g /spark/nlp/TF-IDF_Linear_SVM/Margin/margin_lsvm_CW.py
