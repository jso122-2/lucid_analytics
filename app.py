import os
from flask import Flask, render_template, jsonify, make_response
from blueprints.churn import churn_bp
from blueprints.nps import nps_bp
from blueprints.media import media_bp
from blueprints.about import about_bp
from blueprints.skeleton import skeleton_bp
from utils.utility_worker import utility_worker, run_in_background
# Import the synchronous hand models loader
from utils.hand_models import load_hand_models_sync

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
    return dict(
        minio_base_url=os.environ.get(
            "MINIO_BASE_URL",
            "https://lucidanalytics-production.up.railway.app/marketing.models/models/"
        )
    )

# Workaround for before_first_request: load hand models once on the first request.
@app.before_request
def load_hand_models_once():
    if not app.config.get("HAND_MODELS_LOADED", False):
        try:
            # Synchronously load the hand models using the utility function.
            app.config['HAND_MODELS'] = load_hand_models_sync()
            app.config["HAND_MODELS_LOADED"] = True
            app.logger.info("Hand models loaded successfully.")
        except Exception as e:
            app.logger.error("Failed to load hand models on startup: %s", e)
            app.config['HAND_MODELS'] = {}

@app.route('/hand-models', methods=['GET'])
def get_hand_models():
    """
    Return the hand model URLs loaded synchronously at startup.
    """
    models = app.config.get('HAND_MODELS', {})
    return jsonify(models)

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
    # Replace 'your_heavy_function', 'param1', and 'param2' with actual values or remove this route if unused.
    utility_worker.add_task(your_heavy_function, param1, param2)
    return "Task is running in the background!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
