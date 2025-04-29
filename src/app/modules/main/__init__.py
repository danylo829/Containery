from flask import Blueprint
from flask_login import login_required

main = Blueprint('main', __name__)

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

@main.before_request
@login_required
def before_request():
    pass