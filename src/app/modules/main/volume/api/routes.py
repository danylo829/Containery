from flask import jsonify

from app.core.extensions import docker
from app.modules.user.models import Permissions
from app.core.decorators import permission
from app.lib.common import bytes_to_human_readable

from . import api

@api.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.VOLUME_INFO)
def delete(id):
    response, status_code = docker.delete_volume(id)
    return str(response), status_code

@api.route('/prune', methods=['POST'])
@permission(Permissions.VOLUME_DELETE)
def prune():
    response, status_code = docker.prune_volumes()

    volumes_deleted_list = response.json().get('VolumesDeleted')
    volumes_deleted = len(volumes_deleted_list) if volumes_deleted_list is not None else 0

    if volumes_deleted == 0:
        return jsonify({"message": "Nothing to prune"}), status_code

    space_reclaimed = bytes_to_human_readable(response.json().get('SpaceReclaimed', 0))
    
    message = f"Deleted {volumes_deleted} volumes, reclaimed {space_reclaimed}"
    
    return jsonify({"message": message}), status_code
