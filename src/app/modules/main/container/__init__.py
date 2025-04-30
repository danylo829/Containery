from flask import Blueprint

container = Blueprint('container', __name__, template_folder='templates', static_folder='static')

from .api import api
container.register_blueprint(api, url_prefix='/api')

from . import routes