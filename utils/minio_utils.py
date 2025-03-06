import boto3
import os
from botocore.exceptions import ClientError
from tempfile import NamedTemporaryFile
import pandas as pd
from utils.logger_config import logger

# Fetch MinIO credentials
BUCKET_NAME = os.environ.get("MINIO_BUCKET", "marketing.models")

def get_s3_client():
    endpoint = os.environ.get("MINIO_ENDPOINT", os.environ.get("MINIO_BASE_URL", "minio:9000"))
    logger.info(f"[DEBUG] Using MINIO_ENDPOINT: {endpoint}")
    use_ssl = os.environ.get("MINIO_USE_SSL", "false").lower() == "true"
    protocol = "https" if use_ssl else "http"
    return boto3.client(
        "s3",
        endpoint_url=f"{protocol}://{endpoint}",
        aws_access_key_id=os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
        aws_secret_access_key=os.environ.get("MINIO_SECRET_KEY", "minioadmin"),
        region_name="us-east-1",
    )

def download_hand_model(model_name: str) -> str:
    try:
        temp_file = NamedTemporaryFile(delete=False, suffix=".glb")
        get_s3_client().download_file(BUCKET_NAME, model_name, temp_file.name)
        logger.info(f"✅ Downloaded {model_name} from MinIO to {temp_file.name}")
        return temp_file.name
    except ClientError as e:
        logger.error(f"❌ Error downloading {model_name}: {e}")
        raise FileNotFoundError(f"❌ Unable to download {model_name} from MinIO")

def download_model_from_minio(object_key: str) -> str:
    try:
        temp_file = NamedTemporaryFile(delete=False)
        get_s3_client().download_file(BUCKET_NAME, object_key, temp_file.name)
        logger.info(f"Downloaded {object_key} from MinIO to temporary file {temp_file.name}.")
        return temp_file.name
    except ClientError as e:
        error_message = f"Unable to download {object_key} from bucket {BUCKET_NAME}: {e}"
        logger.error(error_message)
        raise FileNotFoundError(error_message)

def get_presigned_url(object_key: str, expiration: int = 3600) -> str:
    try:
        client = get_s3_client()
        url = client.generate_presigned_url(
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

def get_hand_models(expiration: int = 3600) -> dict:
    try:
        skeleton_model_url = get_presigned_url("skeleton_hand.glb", expiration)
        flesh_model_url = get_presigned_url("flesh_hand.glb", expiration)
        logger.info("Successfully generated pre-signed URLs for both hand models.")
        return {
            "skeleton_model": skeleton_model_url,
            "flesh_model": flesh_model_url
        }
    except Exception as e:
        logger.error("Error generating hand model URLs: %s", e)
        raise e
