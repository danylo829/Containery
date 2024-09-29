from flask import Blueprint, request, redirect, flash, url_for
from flask_login import login_required
from app.utils.docker import Docker
from app.models import Role
from app.decorators import role

api = Blueprint('container', __name__)

docker = Docker()

@api.before_request
@login_required
def before_request():
    pass

@api.route('/<id>/restart', methods=['POST'])
@role([Role.READER], allow=False)
def restart(id):
    respone, status_code = docker.restart_container(id)
    return str(respone), status_code

@api.route('/<id>/start', methods=['POST'])
@role([Role.READER], allow=False)
def start(id):
    response, status_code = docker.start_container(id)
    return str(response), status_code

@api.route('/<id>/stop', methods=['POST'])
@role([Role.READER], allow=False)
def stop(id):
    response, status_code = docker.stop_container(id)
    return str(response), status_code

@api.route('/<id>/delete', methods=['DELETE'])
@role([Role.READER], allow=False)
def delete(id):
    response, status_code = docker.delete_container(id)
    return str(response), status_code
