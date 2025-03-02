# final_webapp/blueprints/skeleton.py
from flask import Blueprint, render_template
from config import MINIO_ASSET_BASE_URL  # from config.py

skeleton_bp = Blueprint('skeleton', __name__)

@skeleton_bp.route('/')
def skeleton_home():
    """
    Render the skeleton page and pass the MinIO asset base URL
    so that the client-side code can load the two GLB files.
    """
    return render_template('skeleton.html', minio_base_url=MINIO_ASSET_BASE_URL)
