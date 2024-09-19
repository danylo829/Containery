from flask import Blueprint

main = Blueprint('main', __name__, static_folder='static', static_url_path='/static/main')

from .dashboard.routes import dashboard
from .container.routes import container
from .image.routes import image
from .volume.routes import volume
from .network.routes import network

main.register_blueprint(dashboard, url_prefix='/dashboard')
main.register_blueprint(container, url_prefix='/container')
main.register_blueprint(image, url_prefix='/image')
main.register_blueprint(volume, url_prefix='/volume')
main.register_blueprint(network, url_prefix='/network')