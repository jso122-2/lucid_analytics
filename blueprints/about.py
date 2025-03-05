from flask import Blueprint, render_template

about_bp = Blueprint('about', __name__, template_folder='../templates')

# This route will match both '/about' and '/about/' without redirecting
@about_bp.route('/', strict_slashes=False)
def about():
    return render_template('about.html')
