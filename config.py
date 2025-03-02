import os
import pandas as pd
import pickle

if os.path.exists("/app/models"):
    BASE_PATH = "/app/models"
    os.environ["CHURN_MODEL_PATH"] = "/app/models/churn_model_20250225_175647.pkl"
    os.environ["CHURN_SCALER_PATH"] = "/app/models/minmax_scaler.pkl"
    os.environ["CHURN_REP_SAMPLE_PATH"] = "/app/models/churn_representative_sample.csv"
    os.environ["INFERENCE_FEATURES_CHURN_PATH"] = "/app/models/inference_features_churn.txt"
    os.environ["INFERENCE_FEATURES_SURVIVAL_PATH"] = "/app/models/inference_features_survival.txt"
    os.environ["CHURN_SURVIVAL_SCALER_PATH"] = "/app/models/minmax_scaler_survival.pkl"
    # Updated Survival model paths for churn:
    os.environ["CHURN_COX_MODEL_PATH"] = "/app/models/churn_cox_model_20250225_172025.pkl"
    os.environ["CHURN_RSF_MODEL_PATH"] = "/app/models/churn_rsf_model.pkl"

    MODEL_PATH = os.environ["CHURN_MODEL_PATH"]
    SCALER_PATH = os.environ["CHURN_SCALER_PATH"]
    CHURN_REP_SAMPLE_PATH = os.environ["CHURN_REP_SAMPLE_PATH"]
    INFERENCE_FEATURES_CHURN_PATH = os.environ["INFERENCE_FEATURES_CHURN_PATH"]
    INFERENCE_FEATURES_SURVIVAL_PATH = os.environ["INFERENCE_FEATURES_SURVIVAL_PATH"]
    CHURN_SURVIVAL_SCALER_PATH = os.environ["CHURN_SURVIVAL_SCALER_PATH"]
    CHURN_COX_MODEL_PATH = os.environ["CHURN_COX_MODEL_PATH"]
    CHURN_RSF_MODEL_PATH = os.environ["CHURN_RSF_MODEL_PATH"]
else:
    BASE_PATH = os.path.join(os.getcwd(), "models")
    MODEL_PATH = os.environ.get("CHURN_MODEL_PATH", os.path.join(BASE_PATH, "churn_model_20250225_175647.pkl"))
    SCALER_PATH = os.environ.get("CHURN_SCALER_PATH", os.path.join(BASE_PATH, "minmax_scaler.pkl"))
    CHURN_REP_SAMPLE_PATH = os.environ.get("CHURN_REP_SAMPLE_PATH", os.path.join(BASE_PATH, "churn_representative_sample.csv"))
    INFERENCE_FEATURES_CHURN_PATH = os.environ.get("INFERENCE_FEATURES_CHURN_PATH", os.path.join(BASE_PATH, "inference_features_churn.txt"))
    INFERENCE_FEATURES_SURVIVAL_PATH = os.environ.get("INFERENCE_FEATURES_SURVIVAL_PATH", os.path.join(BASE_PATH, "inference_features_survival.txt"))
    CHURN_SURVIVAL_SCALER_PATH = os.environ.get("CHURN_SURVIVAL_SCALER_PATH", os.path.join(BASE_PATH, "minmax_scaler_survival.pkl"))
    CHURN_COX_MODEL_PATH = os.environ.get("CHURN_COX_MODEL_PATH", os.path.join(BASE_PATH, "churn_cox_model_20250225_172025.pkl"))
    CHURN_RSF_MODEL_PATH = os.environ.get("CHURN_RSF_MODEL_PATH", os.path.join(BASE_PATH, "churn_rsf_model.pkl"))

# Other model paths remain unchanged:
NPS_MODEL_PATH = os.environ.get("NPS_MODEL_PATH", os.path.join(BASE_PATH, "nps_model.pkl"))
NPS_SCALER_PATH = os.environ.get("NPS_SCALER_PATH", os.path.join(BASE_PATH, "nps_scaler.pkl"))
MEDIA_MODEL_PATH = os.environ.get("MEDIA_MODEL_PATH", os.path.join(BASE_PATH, "media_model_20250219_002020.pkl"))
MEDIA_SCALER_PATH = os.environ.get("MEDIA_SCALER_PATH", os.path.join(BASE_PATH, "standard_scaler.pkl"))

# New configuration for assets stored in MinIO
# This URL should point to the bucket and the prefix where your assets (GLB files, SVGs, etc.) are stored.
MINIO_ASSET_BASE_URL = os.environ.get(
    "MINIO_ASSET_BASE_URL", "http://127.0.0.1:9000/marketing.models/models/"
)
