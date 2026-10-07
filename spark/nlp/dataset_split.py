import os
import logging
from functools import reduce
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

URL_S3_SILVER = os.environ.get("URL_S3_SILVER")
SPLIT_BASE_PATH = f"{URL_S3_SILVER}/sentiment_splits"

CATEGORIES = ["All_Beauty", "Amazon_Fashion"]
SPLIT_RATIOS = [0.70, 0.15, 0.15]  # Train, Validation, Test
SEED = 42

def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName("Dataset_Stratified_Split")
        .master(os.environ.get("SPARK_MASTER_URL", "spark://spark-master:7077"))
        .config(
            "spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262",
        )
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.access.key", os.environ.get("ACCESS_KEY"))
        .config("spark.hadoop.fs.s3a.secret.key", os.environ.get("SECRET_KEY"))
        .config(
            "spark.hadoop.fs.s3a.endpoint",
            os.environ.get("MINIO_ENDPOINT", "http://minio:9000"),
        )
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .getOrCreate()
    )

def stratified_split(df, label_col="label", ratios=[0.70, 0.15, 0.15], seed=42):
    labels = [row[label_col] for row in df.select(label_col).distinct().collect()]
    train_dfs, val_dfs, test_dfs = [], [], []

    for lbl in labels:
        df_lbl = df.filter(F.col(label_col) == lbl)
        train_part, val_part, test_part = df_lbl.randomSplit(ratios, seed=seed)
        train_dfs.append(train_part)
        val_dfs.append(val_part)
        test_dfs.append(test_part)

    train_all = reduce(lambda a, b: a.unionByName(b), train_dfs)
    val_all = reduce(lambda a, b: a.unionByName(b), val_dfs)
    test_all = reduce(lambda a, b: a.unionByName(b), test_dfs)

    return train_all, val_all, test_all

def log_split_stats(logger, split_name: str, df):
    total = df.count()
    stats = df.groupBy("label").count().collect()
    breakdown = ", ".join([f"Class {int(row['label'])}: {row['count']} ({row['count']/total*100:.2f}%)" for row in sorted(stats, key=lambda x: x["label"])])
    logger.info(f"   [{split_name}] Total: {total:,} rows | Breakdown: {breakdown}")

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("DatasetSplitter")

    spark = create_spark_session()
    try:
        for category in CATEGORIES:

            input_path = f"{URL_S3_SILVER}/reviews/{category}"
            df = spark.read.parquet(input_path)

            if "category" not in df.columns:
                df = df.withColumn("category", F.lit(category))

            train_df, val_df, test_df = stratified_split(df, label_col="label", ratios=SPLIT_RATIOS, seed=SEED)

            log_split_stats(logger, "TRAIN", train_df)
            log_split_stats(logger, "VAL  ", val_df)
            log_split_stats(logger, "TEST ", test_df)

            # Save MinIO Silver Layer
            splits = {
                "train": train_df,
                "val": val_df,
                "test": test_df,
            }

            for split_name, split_data in splits.items():
                target_path = f"{SPLIT_BASE_PATH}/{category}/{split_name}"
                (
                    split_data.write
                    .mode("overwrite")
                    .parquet(target_path)
                )


    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()

"""
docker exec -it spark-master spark-submit /spark/nlp/dataset_split.py
"""
