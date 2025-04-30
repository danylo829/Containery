from app.core.extensions import docker
from app.modules.user.models import Permissions
from app.core.decorators import permission

from . import api

@api.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.NETWORK_INFO)
def delete(id):
    response, status_code = docker.delete_network(id)
    return str(response), status_code
