from flask import Blueprint, render_template
import pandas as pd

home_bp = Blueprint('home', __name__, template_folder='../templates')

@home_bp.route('/')
def home():
    # Render the home page which contains your interactive dashboard.
    return render_template('home.html')
