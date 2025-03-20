from flask import Blueprint, request, redirect, flash, url_for

from app.utils.docker import Docker
from app.models import Permissions
from app.decorators import permission

api = Blueprint('container', __name__)

docker = Docker()

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
