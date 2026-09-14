import os
import boto3
from botocore.client import Config
from datasets import load_dataset
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
MINIO_API_HOST = os.environ.get("MINIO_API_HOST")
S3_BUCKET = os.environ.get("S3_BUCKET")

categoricals = ["All_Beauty", "Amazon_Fashion"]

# Create s3_client
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_API_HOST,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
)


def create_bucket(bucket_name):
    try:
        s3_client.create_bucket(Bucket=bucket_name)  # Bucket = keyword arrguments
        print(f"Bucket {bucket_name} created successfully.")
    except Exception as e:
        print(f"Error: {e}")
        pass


create_bucket(S3_BUCKET)

for categorical in categoricals:
    try:
        dataset_review = load_dataset(
            "McAuley-Lab/Amazon-Reviews-2023",
            f"raw_review_{categorical}",
            trust_remote_code=True,
        )
        dataset_review["full"].to_json(f"amazon_reviews_{categorical}_2023.jsonl.gz")  # type: ignore
        temp_file_review = f"amazon_reviews_{categorical}_2023.jsonl.gz"
        s3_key_reviews = f"bronze/reviews/{temp_file_review}"

        # push file into bucket
        s3_client.upload_file(temp_file_review, S3_BUCKET, s3_key_reviews)
        print("Upload reviews successfully")

        # Clear file temp
        if os.path.exists(temp_file_review):
            os.remove(temp_file_review)

        dataset_metadata = load_dataset(
            "McAuley-Lab/Amazon-Reviews-2023",
            f"raw_meta_{categorical}",
            trust_remote_code=True,
        )
        dataset_metadata["full"].to_json(f"amazon_meta_{categorical}_2023.jsonl.gz")  # type: ignore
        temp_file_meta = f"amazon_meta_{categorical}_2023.jsonl.gz"
        s3_key_metadata = f"bronze/metadata/{temp_file_meta}"

        # push file into bucket
        s3_client.upload_file(temp_file_meta, S3_BUCKET, s3_key_metadata)
        print("Upload metadata successfully")

        # Clear file temp
        if os.path.exists(temp_file_meta):
            os.remove(temp_file_meta)

    except Exception as e:
        print(f"Error: {e}")
