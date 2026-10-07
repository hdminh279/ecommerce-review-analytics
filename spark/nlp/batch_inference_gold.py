import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import FloatType
from pyspark.ml import PipelineModel

URL_S3_SILVER = os.environ.get("URL_S3_SILVER", "s3a://amazon-reviews-datalake/silver")
URL_S3_GOLD = os.environ.get("URL_S3_GOLD", "s3a://amazon-reviews-datalake/gold")
MODEL_SAVE_PATH = os.environ.get("MODEL_SAVE", "s3a://amazon-reviews-datalake/silver/model")
BINARY_MODEL_PATH = f"{MODEL_SAVE_PATH}/sentiment_binary_lsvm/class_weighting"
GOLD_FACT_PATH = f"{URL_S3_GOLD}/fact_review_sentiment"

CATEGORIES = ["All_Beauty", "Amazon_Fashion"]
CHOSEN_THETA = 0.30  # Margin threshold (Confidence <= 57.44% mapped to UNCERTAIN)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("Task5_Batch_Inference_Gold")

    try:
        spark = (
            SparkSession.builder.appName("Sentiment_Task5_Batch_Inference_Gold_Fact")
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
            .config("spark.sql.parquet.compression.codec", "snappy")
            .getOrCreate()
        )
        logger.info("Spark Session created successfully.")

        # 1. Load trained Binary Linear SVM PipelineModel
        logger.info(f"Loading Binary Linear SVM model from: {BINARY_MODEL_PATH}")
        binary_model = PipelineModel.load(BINARY_MODEL_PATH)
        logger.info("Binary Linear SVM PipelineModel loaded successfully.")

        # 2. Read all Silver reviews for both categories
        category_dfs = []
        for cat in CATEGORIES:
            cat_path = f"{URL_S3_SILVER}/reviews/{cat}"
            logger.info(f"Reading Silver reviews for {cat} from: {cat_path}")
            df = spark.read.parquet(cat_path).withColumn("category", F.lit(cat))
            category_dfs.append(df)

        full_reviews_df = category_dfs[0].unionByName(category_dfs[1])
        total_input_count = full_reviews_df.count()
        logger.info(f"Total Silver reviews loaded for batch inference: {total_input_count:,}")

        # 3. Model Inference: transform reviews to extract raw signed margin distance
        logger.info("Running distributed batch inference across full Silver dataset...")
        predictions = binary_model.transform(full_reviews_df)

        # In PySpark LinearSVC, rawPrediction is Vector [-margin, margin]
        extract_margin_udf = F.udf(lambda v: float(v[1]), FloatType())
        pred_df = predictions.withColumn("sentiment_score", extract_margin_udf(F.col("rawPrediction")))

        # 4. Compute Sigmoid Probability and Prediction Confidence
        # P(Positive) = 1 / (1 + exp(-sentiment_score))
        # Confidence = max(P, 1 - P)
        pred_df = pred_df.withColumn(
            "prob_pos",
            1.0 / (1.0 + F.exp(-F.col("sentiment_score")))
        ).withColumn(
            "confidence",
            F.when(F.col("prob_pos") >= 0.5, F.col("prob_pos")).otherwise(1.0 - F.col("prob_pos"))
        )

        # 5. Map Sentiment Label and is_negative Flag using CHOSEN_THETA = 0.30
        # Positive  : sentiment_score >  0.30 (Confidence > 57.44%)
        # Negative  : sentiment_score < -0.30 (Confidence > 57.44%)
        # Uncertain : |sentiment_score| <= 0.30 (Confidence <= 57.44%)
        pred_df = pred_df.withColumn(
            "sentiment",
            F.when(F.col("sentiment_score") > CHOSEN_THETA, "POSITIVE")
            .when(F.col("sentiment_score") < -CHOSEN_THETA, "NEGATIVE")
            .otherwise("UNCERTAIN")
        ).withColumn(
            "is_negative",
            F.when(F.col("sentiment") == "NEGATIVE", 1).otherwise(0)
        )

        # 6. Generate Deterministic Unique review_id
        pred_df = pred_df.withColumn(
            "review_id",
            F.md5(F.concat_ws("_", F.col("parent_asin"), F.col("review_date").cast("string"), F.col("review_text")))
        )

        # 7. Select Target Schema for Gold Fact Table
        gold_fact_df = pred_df.select(
            "review_id",
            "parent_asin",
            "category",
            "review_date",
            "rating",
            "sentiment",
            "sentiment_score",
            "confidence",
            "is_negative"
        )

        # 8. Data Quality and Distribution Checks
        logger.info("Performing Gold Layer Data Quality Checks...")
        gold_count = gold_fact_df.count()
        logger.info(f"Gold Fact total record count: {gold_count:,} (Expected: {total_input_count:,})")
        assert gold_count == total_input_count, f"Row count mismatch: {gold_count} vs {total_input_count}"

        null_check = gold_fact_df.filter(
            F.col("review_id").isNull() |
            F.col("parent_asin").isNull() |
            F.col("category").isNull() |
            F.col("sentiment").isNull() |
            F.col("review_date").isNull()
        ).count()
        logger.info(f"Null records in key columns: {null_check} (Must be 0)")
        assert null_check == 0, "Data Quality Failure: Nulls found in key columns!"

        logger.info("Sentiment Class Distribution in Gold Fact:")
        gold_fact_df.groupBy("category", "sentiment").count().orderBy("category", "sentiment").show(truncate=False)

        # 9. Write to Gold Layer Partitioned by Category
        logger.info(f"Writing Gold Fact Parquet dataset to: {GOLD_FACT_PATH}")
        (
            gold_fact_df.write
            .mode("overwrite")
            .partitionBy("category")
            .parquet(GOLD_FACT_PATH)
        )
        logger.info(f"Successfully saved Gold Fact Table to: {GOLD_FACT_PATH}")

    except Exception as e:
        logger.error(f"Error occurred during Task 5 Batch Inference: {str(e)}", exc_info=True)
        raise
    finally:
        if "spark" in locals():
            spark.stop()
            logger.info("Spark Session stopped.")

# Execution Command:
# docker exec -it spark-master spark-submit --driver-memory 2g --executor-memory 3g /spark/nlp/batch_inference_gold.py
