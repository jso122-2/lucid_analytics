import boto3
import os
from botocore.exceptions import ClientError
from tempfile import NamedTemporaryFile
import pandas as pd
from utils.logger_config import logger

# Fetch MinIO credentials
BUCKET_NAME = os.environ.get("MINIO_BUCKET", "marketing.models")

s3_client = boto3.client(
    "s3",
    endpoint_url=os.environ.get("MINIO_ENDPOINT", "http://minio:9000"),
    aws_access_key_id=os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
    aws_secret_access_key=os.environ.get("MINIO_SECRET_KEY", "minioadmin"),
    region_name="us-east-1",
)

def download_hand_model(model_name):
    """
    Download skeleton or flesh hand model from MinIO and return local file path.
    """
    try:
        temp_file = NamedTemporaryFile(delete=False, suffix=".glb")
        s3_client.download_file(BUCKET_NAME, model_name, temp_file.name)
        logger.info(f"✅ Downloaded {model_name} from MinIO to {temp_file.name}")
        return temp_file.name
    except ClientError as e:
        logger.error(f"❌ Error downloading {model_name}: {e}")
        raise FileNotFoundError(f"❌ Unable to download {model_name} from MinIO")


def download_model_from_minio(object_key):
    """
    Download a file from MinIO using the provided object key and return the local temporary filename.
    If the file cannot be downloaded, raise a FileNotFoundError with details.
    """
    try:
        temp_file = NamedTemporaryFile(delete=False)
        s3_client.download_file(BUCKET_NAME, object_key, temp_file.name)
        logger.info(f"Downloaded {object_key} from MinIO to temporary file {temp_file.name}.")
        return temp_file.name
    except ClientError as e:
        error_message = f"Unable to download {object_key} from bucket {BUCKET_NAME}: {e}"
        logger.error(error_message)
        raise FileNotFoundError(error_message)

def get_presigned_url(object_key, expiration=3600):
    """
    Generate a pre-signed URL for the given object in MinIO.
    This URL can be used by the client to directly access the asset.
    """
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": object_key},
            ExpiresIn=expiration
        )
        logger.info(f"Generated presigned URL for {object_key}: {url}")
        return url
    except ClientError as e:
        error_message = f"Unable to generate presigned URL for {object_key}: {e}"
        logger.error(error_message)
        raise e
