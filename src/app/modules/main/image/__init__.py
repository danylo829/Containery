from flask import Blueprint

from app.core.extensions import docker

image = Blueprint('image', __name__, template_folder='templates', static_folder='static')

from .api.routes import api
image.register_blueprint(api, url_prefix='/api')

from . import routes