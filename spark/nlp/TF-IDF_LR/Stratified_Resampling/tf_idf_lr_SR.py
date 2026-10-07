import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, HashingTF, IDF
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from sklearn.metrics import f1_score, confusion_matrix, classification_report

URL_S3_SILVER = os.environ.get("URL_S3_SILVER", "s3a://amazon-reviews-datalake/silver")
MODEL_SAVE_PATH = os.environ.get("MODEL_SAVE", "s3a://amazon-reviews-datalake/silver/model")

CATEGORIES = ["All_Beauty", "Amazon_Fashion"]

def build_tfidf_lr_pipeline_downsample() -> Pipeline:
    """Create PySpark ML Pipeline: Tokenizer -> HashingTF -> IDF -> LogisticRegression"""
    tokenizer = Tokenizer(inputCol="review_text", outputCol="words")
    hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=2**18)
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    
    lr = LogisticRegression(featuresCol="features", labelCol="label", maxIter=20)
    
    pipeline = Pipeline(stages=[tokenizer, hashingTF, idf, lr])
    return pipeline

def evaluate_and_log_metrics(predictions, split_name: str, logger: logging.Logger):
    """Evaluate multiclass metrics and log detailed classification report."""
    evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction")
    accuracy = evaluator.evaluate(predictions, {evaluator.metricName: "accuracy"})
    weighted_f1 = evaluator.evaluate(predictions, {evaluator.metricName: "f1"})
    precision = evaluator.evaluate(predictions, {evaluator.metricName: "weightedPrecision"})
    recall = evaluator.evaluate(predictions, {evaluator.metricName: "weightedRecall"})

    pred_pd = predictions.select("label", "prediction").toPandas()
    y_true = pred_pd["label"]
    y_pred = pred_pd["prediction"]
    macro_f1 = f1_score(y_true, y_pred, average="macro")

    cm = confusion_matrix(y_true, y_pred)
    report = classification_report(y_true, y_pred, target_names=["Negative (0)", "Neutral (1)", "Positive (2)"], digits=4)

    logger.info(f"==================================================")
    logger.info(f"[{split_name}] Accuracy    : {accuracy:.4f}")
    logger.info(f"[{split_name}] Weighted F1 : {weighted_f1:.4f}")
    logger.info(f"[{split_name}] Precision   : {precision:.4f}")
    logger.info(f"[{split_name}] Recall      : {recall:.4f}")
    logger.info(f"[{split_name}] Macro-F1    : {macro_f1:.4f}")
    logger.info(f"[{split_name}] Classification Report:\n{report}")
    logger.info(f"[{split_name}] Confusion Matrix:\n{cm}")
    logger.info(f"==================================================")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("TFIDF_LR_DownSample_Combined")

    try:
        spark = (
            SparkSession.builder.appName("Sentiment_TFIDF_LR_Training_DownSample_Combined")
            .master(os.environ.get("SPARK_MASTER_URL", "spark://spark-master:7077"))
            .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262")
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
        train_df = spark.read.parquet(train_path)
        logger.info(f"Reading combined Validation data from: {val_path}")
        val_df = spark.read.parquet(val_path)

        # Get label counts on combined training set and calculate fractions
        counts = train_df.groupBy("label").count().collect()
        count_dict = {row["label"]: row["count"] for row in counts}
        min_count = min(count_dict.values())
        logger.info(f"Combined label counts before downsampling: {count_dict}")

        fractions = {label: float(min_count / count) for label, count in count_dict.items()}
        logger.info(f"Downsampling fractions: {fractions}")

        train_df_balanced = train_df.sampleBy("label", fractions=fractions, seed=42).cache()
        cached_count = train_df_balanced.count()
        logger.info(f"Materialized balanced combined Train set: {cached_count:,} rows")

        # Build and train pipeline
        pipeline = build_tfidf_lr_pipeline_downsample()
        logger.info("Fitting TF-IDF + LogisticRegression on balanced Train set...")
        model = pipeline.fit(train_df_balanced)

        logger.info("Generating predictions on combined Validation set...")
        predictions = model.transform(val_df)

        # 1. Evaluate Overall Combined Validation performance
        evaluate_and_log_metrics(predictions, "OVERALL_COMBINED_VAL", logger)

        # 2. Evaluate Category Breakdown to check per-category performance
        for cat in CATEGORIES:
            cat_preds = predictions.filter(F.col("category") == cat)
            evaluate_and_log_metrics(cat_preds, f"CATEGORY_{cat}_VAL", logger)

        # Save single combined model
        model_path = f"{MODEL_SAVE_PATH}/sentiment_tfidf_lr/stratified_resampling"
        model.write().overwrite().save(model_path)
        logger.info(f"Combined model successfully saved to: {model_path}")

    except Exception as e:
        logger.error(f"Error occurred during training: {str(e)}", exc_info=True)
        raise
    finally:
        if "spark" in locals():
            spark.stop()
            logger.info("Spark Session stopped.")

# Execution Command:
# docker exec -it spark-master spark-submit --driver-memory 2g --executor-memory 3g /spark/nlp/TF-IDF_LR/Stratified_Resampling/tf_idf_lr_SR.py
