import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

URL_S3_BRONZE = os.environ.get("URL_S3_BRONZE")
URL_S3_SILVER = os.environ.get("URL_S3_SILVER")

reviews_cols = [
    "parent_asin",  # ID products
    "rating",
    "title",
    "text",
]

def preprocessing_review(spark: SparkSession, category: str) -> "pyspark.sql.DataFrame":
    """
    Load data and preprocessing review from Bronze Layer

    Steps:
        1. Read Jsonl.gzip from Bronze layer
        2. Select necessary columns + drop null, drop Duplicate
        3. Format type of data
        4. Create Label (0: negative, 1: positive)
        5. Concat: tilte + review -> review_text, lowercase, clean
        6. Cast timestamp -> review_date.

    Return: 
        DataFrame with schema:
            parent_asin, rating, title, text, review_text,
            timestamp, helpful_vote, verified_purchase,
            review_date, label
    """

    # Read file from Bronze
    df = spark.read.json(
        f"{URL_S3_BRONZE}/reviews/amazon_reviews_{category}_2023.jsonl.gz"
    )

    # Select necessary columns
    df = df.select(reviews_cols)

    # Drop null in necessary columns
    df = df.dropna(subset=["rating", "text", "parent_asin", "timestamp"])

    # Duplicate preprocessing_review
    df = df.dropDuplicates(subset=["text"])

    # Format type
    df = df.withColumn("rating", F.col("rating").cast("float"))

    # Trim space for tilte and text
    df = df.withColumn(
        "title", F.trim(F.coalesce(F.col("title"), F.lit("")))
    ).withColumn("text", F.trim(F.col("text")))

    # Concat title + text -> review text
    df = df.withColumn("review_text", F.concat_ws(" ", F.col("title"), F.col("text")))

    # Lowercase review_text
    df = df.withColumn("review_text", F.lower(F.col("review_text")))

    # Delete HTML, URLs, numbers, special charater
    df = (
        df.withColumn(
            "review_text",
            F.regexp_replace(F.col("review_text"), "<[^>]*>", ""),  # Delete HTML text
        )
        .withColumn(
            "review_text",
            F.regexp_replace(
                F.col("review_text"), "http\\S+|www\\S+", ""
            ),  # Delete URLs
        )
        .withColumn(
            "review_text",
            F.regexp_replace(F.col("review_text"), "[0-9]", ""),  # Delete numbers
        )
       .withColumn(
            "review_text",
            F.regexp_replace(
                F.col("review_text"), "\\s+", " "
            ),  # Delete special charater
        )
        .withColumn("review_text", F.trim(F.col("review_text")))  # Clear space
    )

    # Cast timestamp (unix timestamp) -> datetime
    df = df.withColumn(
        "review_date", (F.col("timestamp") / 1000).cast("timestamp")
    )  # /1000 because col timestamp in milisecond if not /1000 will be year

    df_final = df.drop("title", "text", "timestamp")

    """
    Columns:
    "parent_asin",  # ID products
    "rating",
    "review_text",
    "review_date",
    """

    return df_final
