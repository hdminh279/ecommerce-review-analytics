import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from review_pre import preprocessing_review
from metadata_pre import preprocessing_metadata

URL_S3_BRONZE = os.environ.get("URL_S3_BRONZE")
URL_S3_SILVER = os.environ.get("URL_S3_SILVER")

categoricals = ["All_Beauty", "Amazon_Fashion"]

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    try:
        spark = (
            SparkSession.builder.appName("ETL_Bronze_to_Silver")
            .master("spark://spark-master:7077")
            .config(
                "spark.jars.packages",
                "org.apache.hadoop:hadoop-aws:3.3.4,"
                "com.amazonaws:aws-java-sdk-bundle:1.12.262",
            )
            .config(
                "spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"
            )
            .config("spark.hadoop.fs.s3a.access.key", os.environ.get("ACCESS_KEY"))
            .config("spark.hadoop.fs.s3a.secret.key", os.environ.get("SECRET_KEY"))
            .config(
                "spark.hadoop.fs.s3a.endpoint",
                os.environ.get("MINIO_ENDPOINT", "http://minio:9000"),
            )
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .getOrCreate()
        )
        logger.info("Spark Session create complete")

        for category in categoricals:
            df_review = preprocessing_review(spark, category)
            df_review.write.parquet(f"{URL_S3_SILVER}/reviews/{category}", mode="overwrite")

            df_meta = preprocessing_metadata(spark, category)
            df_meta.write.parquet(f"{URL_S3_SILVER}/metadata/{category}", mode="overwrite")

        logger.info("Clean data and push to silver layer")

    except Exception as e:
        logger.error(f"Error while run spark: {str(e)}")
    finally:
        if "spark" in locals():
            spark.stop()
            logger.info("Spark stopped")


"""
Run scirpts
docker exec -it spark-master spark-submit --py-files /spark/preprocessing/review_pre.py,/spark/preprocessing/metadata_pre.py /spark/preprocessing/preprocessing.py
"""
