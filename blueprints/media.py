from flask import Blueprint, request, send_file, jsonify, render_template
import numpy as np
import pandas as pd
import pickle
from config import MEDIA_MODEL_PATH, MEDIA_SCALER_PATH  # Using container paths
from utils.graph_utils import generate_spend_vs_roi_curve_image, generate_impressions_vs_engagement_bubble_chart_image

media_bp = Blueprint('media_bp', __name__, template_folder='../templates')

# Expected features for media inference (order must match training and inference_features.txt):
EXPECTED_FEATURES = [
    "log_Spend",
    "Impressions",
    "Clicks",
    "Engagement_Score",
    "Conversion_Rate",
    "ROI",
    "Spend_Engagement",
    "CTR",
    "LogSpend_Conversion"
]



media_bp = Blueprint('media', __name__, template_folder='../templates')

@media_bp.route('/')
def media_home():
    # Render the media page template (which will have controls to update the graphs)
    return render_template('media.html')

@media_bp.route('/spend_vs_roi')
def spend_vs_roi():
    dynamic_input = {
        "ad_spend": request.args.get("ad_spend", 1000)
    }
    prediction = {
        "optimal_spend": request.args.get("optimal_spend", 500),
        "max_roi": request.args.get("max_roi", 3.0),
        "k": request.args.get("k", 0.005)
    }
    img_stream = generate_spend_vs_roi_curve_image(dynamic_input, prediction)
    return send_file(img_stream, mimetype='image/png')


@media_bp.route('/impressions_vs_engagement')
def impressions_vs_engagement():
    dynamic_input = {
        "impressions": request.args.get("impressions", 5000),
        "engagement": request.args.get("engagement", 300),
        "interactions": request.args.get("interactions", 150)
    }
    prediction = {
        "predicted_impressions": request.args.get("predicted_impressions", 5200),
        "predicted_engagement": request.args.get("predicted_engagement", 350),
        "predicted_interactions": request.args.get("predicted_interactions", 180)
    }
    img_stream = generate_impressions_vs_engagement_bubble_chart_image(dynamic_input, prediction)
    return send_file(img_stream, mimetype='image/png')

@media_bp.route('/predict', methods=['POST'])
def predict_media():
    try:
        # Extract raw values from the form
        spend = float(request.form.get("Spend", 5000))
        impressions = float(request.form.get("Impressions", 10000))
        clicks = float(request.form.get("Clicks", 500))
        engagement_score = float(request.form.get("Engagement_Score", 0.8))
        conversion_rate = float(request.form.get("Conversion_Rate", 0.05))
        roi = float(request.form.get("ROI", 1.0))
        
        # Compute derived features
        log_Spend = np.log1p(spend)
        Spend_Engagement = spend * engagement_score
        CTR = clicks / impressions if impressions != 0 else 0
        LogSpend_Conversion = np.log1p(spend) * conversion_rate
        
        # Build the input data dictionary using the expected features
        input_data = {
            "log_Spend": log_Spend,
            "Impressions": impressions,
            "Clicks": clicks,
            "Engagement_Score": engagement_score,
            "Conversion_Rate": conversion_rate,
            "ROI": roi,
            "Spend_Engagement": Spend_Engagement,
            "CTR": CTR,
            "LogSpend_Conversion": LogSpend_Conversion
        }
        
        # Create a DataFrame and enforce the expected column order
        df = pd.DataFrame([input_data])
        df = df[EXPECTED_FEATURES]
        
        # Build the payload for the task
        task_payload = {
            "input_data": df.to_dict(orient="records")[0],
            "model_path": MEDIA_MODEL_PATH,
            "scaler_path": MEDIA_SCALER_PATH
        }
        
        from utils.tasks import media_inference
        task = media_inference.delay(task_payload["input_data"])
        return jsonify({
            "task_id": task.id,
            "message": "Media prediction task submitted successfully."
        }), 202
        
    except Exception as e:
        print("Error during media async prediction:", e)
        return jsonify({"error": str(e)}), 400

@media_bp.route('/status/<task_id>', methods=['GET'])
def media_status(task_id):
    from utils.tasks import celery_app
    task = celery_app.AsyncResult(task_id)
    if task.state == "PENDING":
        response = {"state": task.state, "status": "Pending..."}
    elif task.state == "SUCCESS":
        result = task.result
        if isinstance(result, dict) and "error" in result:
            response = {"state": task.state, "error": result["error"]}
        else:
            response = {"state": task.state, "result": result}
    else:
        response = {"state": task.state, "status": str(task.info)}
    return jsonify(response)
