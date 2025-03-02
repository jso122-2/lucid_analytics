from flask import Blueprint, render_template, request, jsonify, send_file
import pandas as pd
import json
import pickle as pk
from config import MODEL_PATH, SCALER_PATH, CHURN_REP_SAMPLE_PATH, INFERENCE_FEATURES_CHURN_PATH
from utils.graph_utils import (
    generate_heatmap,
    generate_dynamic_churn_funnel_chart,
    generate_churn_funnel_chart_from_prediction,
    generate_km_survival_curve_image
)

churn_bp = Blueprint('churn', __name__, template_folder='../templates')

@churn_bp.route('/')
def churn():
    try:
        rep_df = pd.read_csv(CHURN_REP_SAMPLE_PATH)
        heatmap_img = generate_heatmap(rep_df)
        funnel_img = generate_churn_funnel_chart_from_prediction(50)  # example value
    except Exception as e:
        print("Error generating graphs:", e)
        heatmap_img = None
        funnel_img = None

    return render_template('churn.html', heatmap_img=heatmap_img, funnel_img=funnel_img)

@churn_bp.route('/predict', methods=['POST'])
def predict_churn():
    try:
        customer_tenure = float(request.form.get("Customer_Tenure", 50))
        last_engagement_days = float(request.form.get("Last_Engagement_Days", 30))
        input_data = {
            "Engagement_Score_Change": customer_tenure / (last_engagement_days + 1),
            "Payment_Stability": 1.0,
            "Subscription_Loyalty": customer_tenure / 12,
            "Customer_Tenure": customer_tenure,
            "Last_Engagement_Days": last_engagement_days,
            "Review_Count": float(request.form.get("Review_Count", 10)),
            "Social_Media_Engagement": float(request.form.get("Social_Media_Engagement", 50))
        }
        
        task_payload = {
            "input_data": input_data,
            "inference_features_path": INFERENCE_FEATURES_CHURN_PATH,
            "churn_rep_sample_path": CHURN_REP_SAMPLE_PATH,
            "model_path": MODEL_PATH,
            "scaler_path": SCALER_PATH
        }
    
        from utils.tasks import churn_inference
        task = churn_inference.delay(task_payload)
        return jsonify({
            "id": task.id,
            "message": "Churn prediction task submitted successfully."
        }), 202

    except Exception as e:
        print("Error during async prediction:", e)
        return jsonify({"error": str(e)}), 400

@churn_bp.route('/generate_funnel_from_prediction', methods=['POST'])
def generate_funnel_from_prediction():
    try:
        predicted_percentage = request.form.get("predicted_percentage", None)
        if predicted_percentage is None:
            return jsonify({"error": "predicted_percentage not provided"}), 400
        if "%" in predicted_percentage:
            predicted_percentage = float(predicted_percentage.replace("%", ""))
        else:
            predicted_percentage = float(predicted_percentage)
        from utils.graph_utils import generate_churn_funnel_chart_from_prediction
        funnel_img = generate_churn_funnel_chart_from_prediction(predicted_percentage)
        return jsonify({"funnel_chart": funnel_img})
    except Exception as e:
        return jsonify({"error": str(e)})

@churn_bp.route('/generate_survival_curve', methods=['POST'])
def generate_survival_curve():
    try:
        survival_data_json = request.form.get("survival_data", None)
        input_data_json = request.form.get("input_data", None)
        if survival_data_json:
            survival_data = json.loads(survival_data_json)
            img_stream = generate_km_survival_curve_image(derived_data=survival_data)
        elif input_data_json:
            input_data = json.loads(input_data_json)
            img_stream = generate_km_survival_curve_image(input_data=input_data)
        else:
            raise ValueError("No survival data or input features provided for inference.")
        return send_file(img_stream, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)})

@churn_bp.route('/status/<task_id>', methods=['GET'])
def churn_status(task_id):
    from utils.tasks import celery_app
    task = celery_app.AsyncResult(task_id)
    if task.state in ["PENDING", "STARTED"]:
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
