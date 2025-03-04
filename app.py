import os
from flask import Flask, render_template
from blueprints.churn import churn_bp
from blueprints.nps import nps_bp
from blueprints.media import media_bp
from blueprints.about import about_bp
from blueprints.skeleton import skeleton_bp
from utils.utility_worker import utility_worker, run_in_background


app = Flask(__name__, static_folder="static", template_folder="templates", static_url_path="/static")

cert_path = os.path.join(os.path.dirname(__file__), "cert.pem")
key_path = os.path.join(os.path.dirname(__file__), "key.pem")

# Register blueprints with URL prefixes.
app.register_blueprint(churn_bp, url_prefix='/churn')
app.register_blueprint(nps_bp, url_prefix='/nps')
app.register_blueprint(media_bp, url_prefix="/media", name="media")
app.register_blueprint(about_bp, url_prefix='/about')
app.register_blueprint(skeleton_bp, url_prefix='/skeleton')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/long_task')
def long_task():
    # This function will run in the background without blocking the request.
    utility_worker.add_task(your_heavy_function, param1, param2)
    return "Task is running in the background!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


