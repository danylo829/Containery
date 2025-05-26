from flask import Blueprint
from flask_assets import Bundle
from flask_login import login_required

module_name = __name__.split('.')[-1]
user = Blueprint(module_name, __name__, url_prefix=f'/{module_name}', template_folder='templates', static_folder='static')

@user.before_request
@login_required
def before_request():
    pass

@user.context_processor
def inject_variables():
    return dict(active_page=module_name)

def register_assets(assets):
    css = Bundle(
        "styles/user.css",
        "styles/role.css",
        filters="rcssmin",
        output="dist/css/user.%(version)s.css"
    )
    js = Bundle(
        "js/user_profile.js",
        "js/role.js",
        filters='rjsmin',
        output=f"dist/js/{module_name}.%(version)s.js",
    )

    assets.register(f"{module_name}_css", css)
    assets.register(f"{module_name}_js", js)

from . import routes