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
    css = Bundle(
        "styles/dashboard.css",
        filters='rcssmin',
        output="dist/css/dashboard.%(version)s.css",
    )
    assets.register("dashboard_css", css)
    assets.register("dashboard_js", js)