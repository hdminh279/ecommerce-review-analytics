import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StopWordsRemover, NGram, SQLTransformer, HashingTF, IDF
from pyspark.ml.classification import LinearSVC
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from sklearn.metrics import f1_score, confusion_matrix, classification_report

URL_S3_SILVER = os.environ.get("URL_S3_SILVER", "s3a://amazon-reviews-datalake/silver")
MODEL_SAVE_PATH = os.environ.get("MODEL_SAVE", "s3a://amazon-reviews-datalake/silver/model")

CATEGORIES = ["All_Beauty", "Amazon_Fashion"]

def build_binary_lsvm_pipeline(num_features: int = 2**19) -> Pipeline:
    """
    Build PySpark ML Binary Pipeline with Stopword-Pruned N-grams (Negation Preserved):
    Tokenizer -> StopWordsRemover -> NGram(n=2) -> SQLTransformer (concat) ->
    HashingTF (num_features=524,288) -> IDF -> LinearSVC (native binary classifier)
    """
    tokenizer = Tokenizer(inputCol="review_text", outputCol="raw_words")
    
    # Strip non-informative stopword noise while strictly preserving negation words
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
    
    # Native binary LinearSVC supports weightCol directly without OneVsRest wrapper
    lsvc = LinearSVC(
        featuresCol="features",
        labelCol="label",
        weightCol="class_weight",
        maxIter=15,
        regParam=0.1
    )
    
    pipeline = Pipeline(stages=[tokenizer, stop_remover, ngram, sql_transformer, hashingTF, idf, lsvc])
    return pipeline

def evaluate_and_log_binary_metrics(predictions, split_name: str, logger: logging.Logger):
    """Evaluate binary classification metrics and log detailed classification report."""
    evaluator_acc = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
    evaluator_f1 = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="f1")
    evaluator_roc = BinaryClassificationEvaluator(labelCol="label", rawPredictionCol="rawPrediction", metricName="areaUnderROC")

    accuracy = evaluator_acc.evaluate(predictions)
    weighted_f1 = evaluator_f1.evaluate(predictions)
    roc_auc = evaluator_roc.evaluate(predictions)

    pred_pd = predictions.select("label", "prediction").toPandas()
    y_true = pred_pd["label"]
    y_pred = pred_pd["prediction"]
    macro_f1 = f1_score(y_true, y_pred, average="macro")

    cm = confusion_matrix(y_true, y_pred)
    report = classification_report(
        y_true,
        y_pred,
        target_names=["Negative (0)", "Positive (1)"],
        digits=4
    )

    logger.info("==================================================")
    logger.info(f"[{split_name}] Accuracy    : {accuracy:.4f}")
    logger.info(f"[{split_name}] Weighted F1 : {weighted_f1:.4f}")
    logger.info(f"[{split_name}] Macro-F1    : {macro_f1:.4f}")
    logger.info(f"[{split_name}] ROC-AUC     : {roc_auc:.4f}")
    logger.info(f"[{split_name}] Classification Report:\n{report}")
    logger.info(f"[{split_name}] Confusion Matrix:\n{cm}")
    logger.info("==================================================")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("Binary_LinearSVM_ClassWeight_Combined")

    try:
        spark = (
            SparkSession.builder.appName("Sentiment_Binary_LinearSVM_Training_ClassWeight_Combined")
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

        # Read combined Train and Validation splits from all categories
        train_path = f"{URL_S3_SILVER}/sentiment_splits/*/train"
        val_path = f"{URL_S3_SILVER}/sentiment_splits/*/val"
        logger.info(f"Reading combined Train data from: {train_path}")
        raw_train_df = spark.read.parquet(train_path)
        logger.info(f"Reading combined Validation data from: {val_path}")
        raw_val_df = spark.read.parquet(val_path)

        # Filter out Neutral (label == 1.0), keep only Negative (0.0) and Positive (2.0)
        # Remap labels to binary standard: Negative 0.0 -> 0.0, Positive 2.0 -> 1.0
        logger.info("Filtering out Neutral reviews (label 1.0) for Binary Polarity...")
        train_df = (
            raw_train_df.filter(F.col("label").isin([0.0, 2.0]))
            .withColumn("label", F.when(F.col("label") == 2.0, 1.0).otherwise(0.0))
        )
        val_df = (
            raw_val_df.filter(F.col("label").isin([0.0, 2.0]))
            .withColumn("label", F.when(F.col("label") == 2.0, 1.0).otherwise(0.0))
        )

        train_count = train_df.count()
        val_count = val_df.count()
        logger.info(f"Binary Train dataset size     : {train_count:,} rows")
        logger.info(f"Binary Validation dataset size: {val_count:,} rows")

        # Calculate binary class weights on training set
        class_counts = train_df.groupBy("label").count().collect()
        num_classes = len(class_counts)
        weight_dict = {row["label"]: train_count / (num_classes * row["count"]) for row in class_counts}
        logger.info(f"Calculated binary class weights: {weight_dict}")

        mapping_expr = F.create_map([F.lit(x) for pair in weight_dict.items() for x in pair])
        train_df_weighted = train_df.withColumn("class_weight", mapping_expr[F.col("label")])

        # Build and train binary N-gram pipeline
        pipeline = build_binary_lsvm_pipeline(num_features=2**19)
        logger.info("Fitting Binary N-gram (1,2) + Linear SVM (Class Weighting) on Train set...")
        model = pipeline.fit(train_df_weighted)

        logger.info("Generating predictions on Binary Validation set...")
        predictions = model.transform(val_df)

        # 1. Evaluate Overall Combined Validation performance
        evaluate_and_log_binary_metrics(predictions, "OVERALL_COMBINED_BINARY_VAL", logger)

        # 2. Evaluate Category Breakdown to check per-category performance
        for cat in CATEGORIES:
            cat_preds = predictions.filter(F.col("category") == cat)
            evaluate_and_log_binary_metrics(cat_preds, f"CATEGORY_{cat}_BINARY_VAL", logger)

        # Save single combined binary model
        model_path = f"{MODEL_SAVE_PATH}/sentiment_binary_lsvm/class_weighting"
        model.write().overwrite().save(model_path)
        logger.info(f"Combined Binary Linear SVM model successfully saved to: {model_path}")

    except Exception as e:
        logger.error(f"Error occurred during training: {str(e)}", exc_info=True)
        raise
    finally:
        if "spark" in locals():
            spark.stop()
            logger.info("Spark Session stopped.")

# Execution Command:
# docker exec -it spark-master spark-submit --driver-memory 2g --executor-memory 3g /spark/nlp/TF-IDF_Linear_SVM/Binary/binary_lsvm_CW.py
