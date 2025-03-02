import os
import joblib
import pandas as pd
import pickle as pk
from utils.minio_utils import download_model_from_minio

def _get_object_key(path):
    # Normalize the path to ensure consistent forward slashes
    normalized_path = path.replace("\\", "/")
    # Get the object prefix from the environment (default to "models/")
    prefix = os.environ.get("MINIO_OBJECT_PREFIX", "models/models/")
    # Extract the basename (e.g., "churn_model_20250220_182726.pkl")
    basename = os.path.basename(normalized_path)
    # Prepend the prefix to build the full object key
    return prefix + basename


def load_churn_artifacts(model_path, scaler_path):
    """
    Load the churn classification model and scaler.
    If the file is not found locally, download it from MinIO.
    """
    if not os.path.exists(model_path):
        object_key = _get_object_key(model_path)
        print(f"Downloading churn model {object_key} from MinIO...")
        model_path = download_model_from_minio(object_key)
    if not os.path.exists(scaler_path):
        object_key = _get_object_key(scaler_path)
        print(f"Downloading churn scaler {object_key} from MinIO...")
        scaler_path = download_model_from_minio(object_key)
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    print("Loaded churn model:", model)
    print("Loaded churn scaler:", scaler)
    return model, scaler


def load_churn_survival_artifacts(cox_model_path, rsf_model_path):

    if not os.path.exists(cox_model_path):
        object_key = _get_object_key(cox_model_path)
        print(f"Downloading churn Cox model {object_key} from MinIO...")
        cox_model_path = download_model_from_minio(object_key)
    if rsf_model_path and not os.path.exists(rsf_model_path):
        object_key = _get_object_key(rsf_model_path)
        print(f"Downloading churn RSF model {object_key} from MinIO...")
        rsf_model_path = download_model_from_minio(object_key)
    
    cox_model = joblib.load(cox_model_path)
    rsf_model = joblib.load(rsf_model_path) if rsf_model_path else None
    print("Loaded churn Cox model:", cox_model)
    if rsf_model is not None:
        print("Loaded churn RSF model:", rsf_model)
    return cox_model, rsf_model




def load_nps_artifacts(model_path, scaler_path):
    """
    Load the NPS model and scaler.
    If the file is not found locally, download it from MinIO.
    """
    if not os.path.exists(model_path):
        object_key = _get_object_key(model_path)
        print(f"Downloading NPS model {object_key} from MinIO...")
        model_path = download_model_from_minio(object_key)
    if not os.path.exists(scaler_path):
        object_key = _get_object_key(scaler_path)
        print(f"Downloading NPS scaler {object_key} from MinIO...")
        scaler_path = download_model_from_minio(object_key)
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    print("Loaded NPS model:", model)
    print("Loaded NPS scaler:", scaler)
    return model, scaler


def load_media_artifacts(model_path, scaler_path):
    """
    Load the media model and scaler.
    If the file is not found locally, download it from MinIO.
    """
    if not os.path.exists(model_path):
        object_key = _get_object_key(model_path)
        print(f"Downloading media model {object_key} from MinIO...")
        model_path = download_model_from_minio(object_key)
    if not os.path.exists(scaler_path):
        object_key = _get_object_key(scaler_path)
        print(f"Downloading media scaler {object_key} from MinIO...")
        scaler_path = download_model_from_minio(object_key)
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    print("Loaded media model:", model)
    print("Loaded media scaler:", scaler)
    return model, scaler


def load_inference_features(path):
    """
    Load inference features from a text file.
    Returns a list of feature names.
    If the file does not exist locally, download it from MinIO.
    """
    if not os.path.exists(path):
        object_key = _get_object_key(path)
        print(f"Downloading inference features file {object_key} from MinIO...")
        path = download_model_from_minio(object_key)
    with open(path, "r") as f:
        features = [line.strip() for line in f if line.strip()]
    return features


def load_representative_sample(path):
    """
    Load a representative sample from a CSV file.
    Returns the data in JSON format (records orientation).
    If the file does not exist locally, download it from MinIO.
    """
    if not os.path.exists(path):
        object_key = _get_object_key(path)
        print(f"Downloading representative sample file {object_key} from MinIO...")
        path = download_model_from_minio(object_key)
    df = pd.read_csv(path)
    return df.to_json(orient="records")
