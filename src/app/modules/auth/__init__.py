from flask import Blueprint
from flask_assets import Bundle

module_name = __name__.split('.')[-1]
auth = Blueprint(module_name, __name__, url_prefix=f'/{module_name}', template_folder='templates', static_folder='static')

def register_assets(assets):
    css = Bundle(
        f"styles/{module_name}.css",
        filters="rcssmin",
        output=f"dist/css/{module_name}.%(version)s.css"
    )
    assets.register(f"{module_name}_css", css)

from . import routes