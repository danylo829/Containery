from flask import Blueprint

volume = Blueprint('volume', __name__, template_folder='templates', static_folder='static')

from .api.routes import api
volume.register_blueprint(api, url_prefix='/api')

from . import routes