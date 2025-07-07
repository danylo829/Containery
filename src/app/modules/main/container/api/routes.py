from flask import jsonify

from app.core.extensions import docker
from app.modules.user.models import Permissions
from app.core.decorators import permission
from app.lib.common import bytes_to_human_readable

from . import api

@api.route('/<id>/restart', methods=['POST'])
@permission(Permissions.CONTAINER_RESTART)
def restart(id):
    respone, status_code = docker.restart_container(id)
    return str(respone), status_code

@api.route('/<id>/start', methods=['POST'])
@permission(Permissions.CONTAINER_START)
def start(id):
    response, status_code = docker.start_container(id)
    return str(response), status_code

@api.route('/<id>/stop', methods=['POST'])
@permission(Permissions.CONTAINER_STOP)
def stop(id):
    response, status_code = docker.stop_container(id)
    return str(response), status_code

@api.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.CONTAINER_DELETE)
def delete(id):
    response, status_code = docker.delete_container(id)
    return str(response), status_code

@api.route('/prune', methods=['POST'])
@permission(Permissions.CONTAINER_DELETE)
def prune():
    response, status_code = docker.prune_containers()

    containers_deleted_list = response.json().get('ContainersDeleted')
    containers_deleted = len(containers_deleted_list) if containers_deleted_list is not None else 0

    if containers_deleted == 0:
        return jsonify({"message": "Nothing to prune"}), status_code

    space_reclaimed = bytes_to_human_readable(response.json().get('SpaceReclaimed', 0))
    
    message = f"Deleted {containers_deleted} containers, reclaimed {space_reclaimed}"
    
    return jsonify({"message": message}), status_code
