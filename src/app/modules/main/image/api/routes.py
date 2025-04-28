from flask import Blueprint, current_app

from app.core.extensions import docker
from app.modules.user.models import Permissions
from app.core.decorators import permission

api = Blueprint('image', __name__)

@api.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.IMAGE_INFO)
def delete(id):
    response, status_code = docker.delete_image(id)
    return str(response), status_code
