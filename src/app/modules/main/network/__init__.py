from flask import Blueprint

network = Blueprint('network', __name__, template_folder='templates', static_folder='static')

from .api.routes import api
network.register_blueprint(api, url_prefix='/api')

from . import routes