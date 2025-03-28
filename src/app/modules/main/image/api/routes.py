from flask import Blueprint

from app.utils.docker import Docker
from app.models import Permissions
from app.decorators import permission

api = Blueprint('image', __name__)

docker = Docker()

@api.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.IMAGE_INFO)
def delete(id):
    response, status_code = docker.delete_image(id)
    return str(response), status_code
