from flask import Blueprint
from flask_assets import Bundle

dashboard = Blueprint('dashboard', __name__, template_folder='templates', static_folder='static')

from . import routes

def register_assets(assets):
    js = Bundle(
        "js/dashboard.js",
        filters='rjsmin',
        output="dist/js/dashboard.%(version)s.js",
    )
    assets.register("dashboard_js", js)