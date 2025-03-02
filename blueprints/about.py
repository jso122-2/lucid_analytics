from flask import Blueprint, render_template
import pandas as pd


about_bp = Blueprint('about', __name__, template_folder='../templates')

@about_bp.route('/about')
def about():
    # Render the graphing and about section.
    return render_template('about.html')
