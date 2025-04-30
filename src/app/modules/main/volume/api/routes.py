from app.core.extensions import docker
from app.modules.user.models import Permissions
from app.core.decorators import permission

from . import api

@api.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.VOLUME_INFO)
def delete(id):
    response, status_code = docker.delete_volume(id)
    return str(response), status_code
