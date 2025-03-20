from flask import Blueprint

from app.utils.docker import Docker
from app.models import Permissions
from app.decorators import permission

api = Blueprint('network', __name__)

docker = Docker()

@api.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.NETWORK_INFO)
def delete(id):
    response, status_code = docker.delete_network(id)
    return str(response), status_code
