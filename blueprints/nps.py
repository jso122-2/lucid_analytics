from flask import Blueprint, render_template, request, send_file, jsonify
import json

from utils.graph_utils import (
    generate_predicted_nps_bubble_chart_image,
    generate_predicted_nps_density_plot_image
)

nps_bp = Blueprint('nps', __name__, template_folder='../templates')

@nps_bp.route('/')
def nps():
    return render_template('nps.html')

@nps_bp.route('/predict', methods=['POST'])
def predict_nps():
    try:
        # Extract input values from the form.
        spend = float(request.form.get("spend", 10000))
        acquisition_cost = float(request.form.get("acquisition_cost", 200))
        engagement_score = float(request.form.get("engagement_score", 0.8))
        impressions = float(request.form.get("impressions", 5000))
        revenue = float(request.form.get("revenue", 15000))
        conversions = float(request.form.get("conversions", 250))
        spend_impressions_interaction = float(request.form.get("spend_impressions_interaction", 1.5))
        
        input_data = {
            "Spend": spend,
            "Acquisition_Cost": acquisition_cost,
            "Engagement_Score": engagement_score,
            "Impressions": impressions,
            "Revenue": revenue,
            "Conversions": conversions,
            "Spend_Impressions_Interaction": spend_impressions_interaction
        }
        
        # (Optional) Convert to DataFrame if needed.
        import pandas as pd
        df = pd.DataFrame([input_data])
        
        # Call your asynchronous NPS inference task.
        from utils.tasks import nps_inference
        task = nps_inference.delay(input_data)
        return jsonify({
            "task_id": task.id,
            "message": "NPS prediction task submitted successfully."
        }), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@nps_bp.route('/predicted_bubble_image')
def predicted_bubble_image():
    """
    This endpoint generates the predicted NPS bubble chart as a PNG.
    It expects query parameters:
      spend, revenue, acquisition_cost, engagement_score, impressions,
      conversions, spend_impressions_interaction,
      predicted_spend, predicted_revenue.
    """
    dynamic_input = {
        "spend": request.args.get("spend", 10000),
        "revenue": request.args.get("revenue", 15000),
        "acquisition_cost": request.args.get("acquisition_cost", 200),
        "engagement_score": request.args.get("engagement_score", 0.8),
        "impressions": request.args.get("impressions", 5000),
        "conversions": request.args.get("conversions", 250),
        "spend_impressions_interaction": request.args.get("spend_impressions_interaction", 1.5)
    }
    prediction = {
        "predicted_spend": request.args.get("predicted_spend", 12000),
        "predicted_revenue": request.args.get("predicted_revenue", 17000)
    }
    img_stream = generate_predicted_nps_bubble_chart_image(dynamic_input, prediction)
    return send_file(img_stream, mimetype='image/png')

@nps_bp.route('/predicted_density_image')
def predicted_density_image():
    """
    This endpoint generates the predicted NPS density plot as a PNG.
    It expects query parameters:
      spend, predicted_spend.
    """
    dynamic_input = {
        "spend": request.args.get("spend", 10000)
    }
    prediction = {
        "predicted_spend": request.args.get("predicted_spend", 12000)
    }
    img_stream = generate_predicted_nps_density_plot_image(dynamic_input, prediction)
    return send_file(img_stream, mimetype='image/png')

@nps_bp.route('/status/<task_id>', methods=['GET'])
def nps_status(task_id):
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
