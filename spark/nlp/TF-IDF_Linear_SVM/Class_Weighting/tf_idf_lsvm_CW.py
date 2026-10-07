import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, HashingTF, IDF
from pyspark.ml.classification import LinearSVC, OneVsRest
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from sklearn.metrics import f1_score, confusion_matrix, classification_report

URL_S3_SILVER = os.environ.get("URL_S3_SILVER", "s3a://amazon-reviews-datalake/silver")
MODEL_SAVE_PATH = os.environ.get("MODEL_SAVE", "s3a://amazon-reviews-datalake/silver/model")

CATEGORIES = ["All_Beauty", "Amazon_Fashion"]

def build_tfidf_lsvc_pipeline() -> Pipeline:
    """Create PySpark ML Pipeline: Tokenizer -> HashingTF -> IDF -> OneVsRest(LinearSVC)"""
    tokenizer = Tokenizer(inputCol="review_text", outputCol="words")
    hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=2**18)
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    
    lsvc = LinearSVC(featuresCol="features", labelCol="label", maxIter=15, regParam=0.1)
    our_lsvc = OneVsRest(classifier=lsvc, labelCol="label", featuresCol="features", weightCol="class_weight")
    
    pipeline = Pipeline(stages=[tokenizer, hashingTF, idf, our_lsvc])
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
    logger = logging.getLogger("TFIDF_LinearSVC_ClassWeight_Combined")

    try:
        spark = (
            SparkSession.builder.appName("Sentiment_TFIDF_LinearSVC_Training_ClassWeight_Combined")
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

        # Calculate class weights on combined training set
        total_count = train_df.count()
        class_counts = train_df.groupBy("label").count().collect()
        num_classes = len(class_counts)
        weight_dict = {row["label"]: total_count / (num_classes * row["count"]) for row in class_counts}
        logger.info(f"Calculated combined class weights: {weight_dict}")

        mapping_expr = F.create_map([F.lit(x) for pair in weight_dict.items() for x in pair])
        train_df_weighted = train_df.withColumn("class_weight", mapping_expr[F.col("label")])

        # Build and train pipeline
        pipeline = build_tfidf_lsvc_pipeline()
        logger.info("Fitting TF-IDF + LinearSVC on combined Train set...")
        model = pipeline.fit(train_df_weighted)

        logger.info("Generating predictions on combined Validation set...")
        predictions = model.transform(val_df)

        # 1. Evaluate Overall Combined Validation performance
        evaluate_and_log_metrics(predictions, "OVERALL_COMBINED_VAL", logger)

        # 2. Evaluate Category Breakdown to check per-category performance
        for cat in CATEGORIES:
            cat_preds = predictions.filter(F.col("category") == cat)
            evaluate_and_log_metrics(cat_preds, f"CATEGORY_{cat}_VAL", logger)

        # Save single combined model
        model_path = f"{MODEL_SAVE_PATH}/sentiment_tfidf_lsvm/class_weighting"
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
# docker exec -it spark-master spark-submit --driver-memory 2g --executor-memory 3g /spark/nlp/TF-IDF_Linear_SVM/Class_Weighting/tf_idf_lsvm_CW.py

