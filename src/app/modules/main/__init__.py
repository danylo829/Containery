from flask import Blueprint
from flask_login import login_required

module_name = __name__.split('.')[-1]
main = Blueprint(module_name, __name__)

from . import dashboard, container, image, volume, network

main.register_blueprint(dashboard.dashboard, url_prefix='/dashboard')
main.register_blueprint(container.container, url_prefix='/container')
main.register_blueprint(image.image, url_prefix='/image')
main.register_blueprint(volume.volume, url_prefix='/volume')
main.register_blueprint(network.network, url_prefix='/network')

@main.before_request
@login_required
def before_request():
    pass

def register_assets(assets):
    dashboard.register_assets(assets)
    container.register_assets(assets)
    image.register_assets(assets)
    volume.register_assets(assets)
    network.register_assets(assets)