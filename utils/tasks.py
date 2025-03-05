import os
import sys
import asyncio
import joblib
import pickle
import pandas as pd
from celery import Celery
from xgboost import XGBClassifier
from config import (
    MODEL_PATH, SCALER_PATH, CHURN_REP_SAMPLE_PATH, 
    INFERENCE_FEATURES_CHURN_PATH, INFERENCE_FEATURES_SURVIVAL_PATH,
    NPS_MODEL_PATH, NPS_SCALER_PATH, MEDIA_MODEL_PATH, MEDIA_SCALER_PATH,
    CHURN_COX_MODEL_PATH, CHURN_RSF_MODEL_PATH, CHURN_SURVIVAL_SCALER_PATH
)

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# If running inside Docker, override the environment variables.
if os.path.exists("/app/models"):
    os.environ["CHURN_MODEL_PATH"] = "/app/models/churn_model_20250225_175647.pkl"
    os.environ["CHURN_SCALER_PATH"] = "/app/models/minmax_scaler.pkl"
    os.environ["NPS_MODEL_PATH"] = "/app/models/nps_model.pkl"
    os.environ["NPS_SCALER_PATH"] = "/app/models/nps_scaler.pkl"
    os.environ["MEDIA_MODEL_PATH"] = "/app/models/media_model_20250219_002020.pkl"
    os.environ["MEDIA_SCALER_PATH"] = "/app/models/standard_scaler.pkl"
    os.environ["CHURN_COX_MODEL_PATH"] = "/app/models/churn_cox_model_20250225_172025.pkl"
    os.environ["CHURN_RSF_MODEL_PATH"] = "/app/models/churn_rsf_model.pkl"

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://default:KBXiFjDBNmVsKuwvHzgBJqOKuQsAsBUI@gondola.proxy.rlwy.net:32201/0")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://default:KBXiFjDBNmVsKuwvHzgBJqOKuQsAsBUI@gondola.proxy.rlwy.net:32201/0")

celery_app = Celery('tasks', broker=broker_url, backend=result_backend)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Global Variables for lazy loading
CHURN_MODEL = None
CHURN_SCALER = None
NPS_MODEL = None
NPS_SCALER = None
MEDIA_MODEL = None
MEDIA_SCALER = None
CHURN_COX_MODEL = None
CHURN_RSF_MODEL = None

BASE_PATH = os.path.join(os.getcwd(), "models")

def get_churn_artifacts():
    global CHURN_MODEL, CHURN_SCALER
    if CHURN_MODEL is None or CHURN_SCALER is None:
        from utils.model_utils import load_churn_artifacts as util_load_churn_artifacts
        CHURN_MODEL, CHURN_SCALER = util_load_churn_artifacts(MODEL_PATH, SCALER_PATH)
    return CHURN_MODEL, CHURN_SCALER

def get_nps_artifacts():
    global NPS_MODEL, NPS_SCALER
    if NPS_MODEL is None or NPS_SCALER is None:
        from utils.model_utils import load_nps_artifacts as util_load_nps_artifacts
        NPS_MODEL, NPS_SCALER = util_load_nps_artifacts(NPS_MODEL_PATH, NPS_SCALER_PATH)
    return NPS_MODEL, NPS_SCALER

def get_media_artifacts():
    global MEDIA_MODEL, MEDIA_SCALER
    if MEDIA_MODEL is None or MEDIA_SCALER is None:
        from utils.model_utils import load_media_artifacts as util_load_media_artifacts
        MEDIA_MODEL, MEDIA_SCALER = util_load_media_artifacts(MEDIA_MODEL_PATH, MEDIA_SCALER_PATH)
    return MEDIA_MODEL, MEDIA_SCALER

def get_churn_survival_artifacts():
    global CHURN_COX_MODEL, CHURN_RSF_MODEL
    if CHURN_COX_MODEL is None or CHURN_RSF_MODEL is None:
        from utils.model_utils import load_churn_survival_artifacts
        CHURN_COX_MODEL, CHURN_RSF_MODEL = load_churn_survival_artifacts(CHURN_COX_MODEL_PATH, CHURN_RSF_MODEL_PATH)
    return CHURN_COX_MODEL, CHURN_RSF_MODEL

celery_app = Celery('tasks', broker=os.environ.get("CELERY_BROKER_URL"), backend=os.environ.get("CELERY_RESULT_BACKEND"))

@celery_app.task
def load_hand_models():
    """
    Fetch skeleton and flesh hand models from MinIO and return URLs.
    """
    from utils.minio_utils import get_presigned_url

    try:
        skeleton_model_url = get_presigned_url("skeleton_hand.glb")
        flesh_model_url = get_presigned_url("flesh_hand.glb")

        return {
            "skeleton_model": skeleton_model_url,
            "flesh_model": flesh_model_url
        }
    except Exception as e:
        return {"error": str(e)}



@celery_app.task
def churn_inference(task_payload: dict):
    import pickle
    from utils.model_utils import load_churn_artifacts, load_inference_features
    import joblib  # for loading scalers
    global CHURN_MODEL, CHURN_SCALER

    # 1) Load classification model and scaler if needed.
    if CHURN_MODEL is None or CHURN_SCALER is None:
        CHURN_MODEL, CHURN_SCALER = load_churn_artifacts(
            task_payload.get("model_path"),
            task_payload.get("scaler_path")
        )
    
    # 2) Load the survival model and its dedicated scaler.
    from config import CHURN_COX_MODEL_PATH, CHURN_SURVIVAL_SCALER_PATH, INFERENCE_FEATURES_SURVIVAL_PATH
    with open(CHURN_COX_MODEL_PATH, "rb") as f:
        survival_model = pickle.load(f)
    survival_scaler = joblib.load(CHURN_SURVIVAL_SCALER_PATH)
    # Load the list of features that the survival model was trained on.
    survival_features = load_inference_features(INFERENCE_FEATURES_SURVIVAL_PATH)
    print("Survival inference features:", survival_features)

    try:
        # -------------------------
        # A) Classification Part
        # -------------------------
        input_data = task_payload.get("input_data", {})
        # For classification, use the churn inference features from the config.
        from config import INFERENCE_FEATURES_CHURN_PATH
        classification_features = load_inference_features(INFERENCE_FEATURES_CHURN_PATH)
        # Build a DataFrame containing only the classification features:
        df_input_class = pd.DataFrame([{feat: input_data.get(feat, 0) for feat in classification_features}])
        print("DF for classification:", df_input_class.columns.tolist(), df_input_class.shape)
        scaled_input = CHURN_SCALER.transform(df_input_class)
        print("Scaled classification input:", scaled_input)
        probs = CHURN_MODEL.predict_proba(scaled_input)
        churn_prob = float(probs[0][1])
        result = {
            "predicted_percentage": f"{round(churn_prob * 100, 2)}%",
            "raw_prob": churn_prob
        }
        
        # -------------------------
        # B) Survival Inference Part
        # -------------------------
        # Build a DataFrame for survival inference using only the pruned features.
        df_input_surv = pd.DataFrame([{feat: input_data.get(feat, 0) for feat in survival_features}])
        print("DF for survival inference:", df_input_surv.columns.tolist(), df_input_surv.head())
        # Scale the survival features using the dedicated survival scaler.
        df_input_surv_scaled = pd.DataFrame(survival_scaler.transform(df_input_surv), columns=survival_features)
        print("DF for survival inference (after scaling):", df_input_surv_scaled.head())
        survival_function = survival_model.predict_survival_function(df_input_surv_scaled)
        survival_data = {
            "T": list(survival_function.index),
            "Survival": list(survival_function.iloc[:, 0])
        }
        result["survival_data"] = survival_data

        return result

    except Exception as e:
        return {"error": str(e)}

@celery_app.task
def nps_inference(input_data: dict):
    try:
        model, scaler = get_nps_artifacts()
        df = pd.DataFrame([input_data])
        print("NPS Inference - DataFrame columns:", df.columns.tolist(), "shape:", df.shape)
        if df.empty or df.shape[1] != 7:
            raise ValueError("Input DataFrame does not have the expected 7 features.")
        scaled_input = scaler.transform(df)
        prob = model.predict_proba(scaled_input)
        positive_class_prob = float(prob[0][1])
        predicted_segment = model.predict(scaled_input)[0]
        result = {
            "predicted_segment": str(predicted_segment),
            "predicted_probability": f"{round(positive_class_prob * 100, 2)}%"
        }
        return result
    except Exception as e:
        return {"error": str(e)}

@celery_app.task
def media_inference(input_data: dict):
    try:
        model, scaler = get_media_artifacts()
        df = pd.DataFrame([input_data])
        print("Media Inference - Input DataFrame:", df)
        scaled_input = scaler.transform(df)
        prediction = model.predict(scaled_input)[0]
        result = {"Predicted_Revenue": float(prediction)}
        print("Media Inference - Result:", result)
        return result
    except Exception as e:
        return {"error": str(e)}

@celery_app.task
def load_all_models():
    results = {
        "churn": get_churn_artifacts(),
        "nps": get_nps_artifacts(),
        "media": get_media_artifacts()
    }
    return results

@celery_app.task
def load_churn_resources():
    try:
        from utils.model_utils import load_inference_features, load_representative_sample
        features = load_inference_features(os.path.join(BASE_PATH, "inference_features_churn.txt"))
        rep_sample = load_representative_sample(os.path.join(BASE_PATH, "churn_representative_sample.csv"))
        return {
            "inference_features": features,
            "churn_representative_sample": rep_sample
        }
    except Exception as e:
        return {"error": str(e)}

@celery_app.task
def load_nps_resources():
    try:
        from utils.model_utils import load_representative_sample
        rep_sample = load_representative_sample(os.path.join(BASE_PATH, "nps_representative_sample.csv"))
        training_df = pd.read_csv(os.path.join(BASE_PATH, "training", "synthetic_media_data.csv"))
        training_data = training_df.to_json(orient="records")
        return {
            "nps_representative_sample": rep_sample,
            "training_data": training_data
        }
    except Exception as e:
        return {"error": str(e)}
