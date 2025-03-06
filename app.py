import os
from flask import Flask, render_template, jsonify, make_response
from blueprints.churn import churn_bp
from blueprints.nps import nps_bp
from blueprints.media import media_bp
from blueprints.about import about_bp
from blueprints.skeleton import skeleton_bp
from utils.utility_worker import utility_worker, run_in_background
from flask import jsonify
from utils.tasks import load_hand_models  # Correct import

app = Flask(__name__, static_folder="static", template_folder="templates", static_url_path="/static")

cert_path = os.path.join(os.path.dirname(__file__), "cert.pem")
key_path = os.path.join(os.path.dirname(__file__), "key.pem")

# Register blueprints.
app.register_blueprint(churn_bp, url_prefix='/churn')
app.register_blueprint(nps_bp, url_prefix='/nps')
app.register_blueprint(media_bp, url_prefix="/media", name="media")
app.register_blueprint(about_bp, url_prefix='/about')
app.register_blueprint(skeleton_bp, url_prefix='/skeleton')

@app.route('/')
def index():
    return render_template('index.html')

@app.context_processor
def inject_minio_url():
    return dict(minio_base_url=os.environ.get("MINIO_BASE_URL", "https://lucidanalytics-production.up.railway.app/marketing.models/models/"))

@app.route('/celery-task/load_hand_models', methods=['POST'])
def celery_load_hand_models():
    task = load_hand_models.delay()
    return jsonify(task_id=task.id)

@app.route('/proxy/<path:object_key>')
def proxy_object(object_key):
    from utils.minio_utils import download_model_from_minio
    try:
        local_file = download_model_from_minio(object_key)
        with open(local_file, "rb") as f:
            data = f.read()
        response = make_response(data)
        response.headers["Content-Type"] = "model/gltf-binary"
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/long_task')
def long_task():
    utility_worker.add_task(your_heavy_function, param1, param2)
    return "Task is running in the background!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
