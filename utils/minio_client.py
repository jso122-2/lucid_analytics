import boto3
import os

# Fetch MinIO credentials from environment variables
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://127.0.0.1:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "marketing.models")

# Configure MinIO client explicitly
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY
)

def download_model(model_name, local_path="/app/models/"):
    """
    Download model from MinIO and save it locally.
    """
    local_file = os.path.join(local_path, model_name)
    
    try:
        s3_client.download_file(MINIO_BUCKET, model_name, local_file)
        print(f"✅ Model {model_name} downloaded successfully.")
        return local_file
    except Exception as e:
        print(f"❌ Error downloading {model_name}: {e}")
        return None
