from flask import jsonify

from app.core.extensions import docker
from app.modules.user.models import Permissions
from app.core.decorators import permission
from app.lib.common import bytes_to_human_readable

from . import api

@api.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.NETWORK_INFO)
def delete(id):
    response, status_code = docker.delete_network(id)
    return str(response), status_code

@api.route('/prune', methods=['POST'])
@permission(Permissions.NETWORK_DELETE)
def prune():
    response, status_code = docker.prune_networks()

    networks_deleted_list = response.json().get('NetworksDeleted')
    networks_deleted = len(networks_deleted_list) if networks_deleted_list is not None else 0

    if networks_deleted == 0:
        return jsonify({"message": "Nothing to prune"}), status_code

    space_reclaimed = bytes_to_human_readable(response.json().get('SpaceReclaimed', 0))
    
    message = f"Deleted {networks_deleted} networks, reclaimed {space_reclaimed}"
    
    return jsonify({"message": message}), status_code
