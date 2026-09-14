import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

URL_S3_BRONZE = os.environ.get("URL_S3_BRONZE")
URL_S3_SILVER = os.environ.get("URL_S3_SILVER")

metadata_cols = [
    "parent_asin",  # ID products
    "main_category",
    "categories",
    "features",
    "details",
    "title",
]

def preprocessing_metadata(spark: SparkSession, category: str) -> "pyspark.sql.DataFrame":
    """
    Load data and preprocessing metadata from Bronze Layer

    Steps:
        1. Read Jsonl.gzip from Bronze layer
        2. Select necessary columns + drop null, drop Duplicate + trim

    Return: 
        DataFrame with schema:
            parent_asin, main_category, categories,
            features, details, title
    """

    # Read file from Bronze
    df = spark.read.json(
        f"{URL_S3_BRONZE}/metadata/amazon_meta_{category}_2023.jsonl.gz"
    )

    # Select necessary columns
    df = df.select(metadata_cols)

    # Drop null in necessary columns
    df = df.dropna(subset=["parent_asin"])

    # Duplicate preprocessing_review
    df = df.dropDuplicates(subset=["parent_asin"])

    # Trim space for tilte and text
    df = df.withColumn(
        "title", F.trim(F.coalesce(F.col("title"), F.lit("")))
    ).withColumn("main_category", F.trim(F.coalesce(F.col("main_category"), F.lit(""))))

    return df
