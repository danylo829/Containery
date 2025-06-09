from flask import Blueprint
from flask_assets import Bundle

module_name = __name__.split('.')[-1]
index = Blueprint(module_name, __name__, template_folder='templates', static_folder='static')

def register_assets(assets):
    css = Bundle(
        f"styles/about.css",
        filters="rcssmin",
        output="dist/css/about.%(version)s.css"
    )

    assets.register("about_css", css)

from . import routes