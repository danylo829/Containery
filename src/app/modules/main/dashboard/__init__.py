from flask import Blueprint
from flask_assets import Bundle

dashboard = Blueprint('dashboard', __name__, template_folder='templates', static_folder='static')

from .api import api
dashboard.register_blueprint(api, url_prefix='/api')

def register_assets(assets):
    js = Bundle(
        "js/dashboard.js",
        filters='rjsmin',
        output="dist/js/dashboard.%(version)s.js",
    )
    js_info = Bundle(
        "js/dashboard_info.js",
        filters='rjsmin',
        output="dist/js/dashboard_info.%(version)s.js",
    )
    css = Bundle(
        "styles/dashboard.css",
        filters='rcssmin',
        output="dist/css/dashboard.%(version)s.css",
    )
    assets.register("dashboard_css", css)
    assets.register("dashboard_js", js)
    assets.register("dashboard_info_js", js_info)

from . import routes