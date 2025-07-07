from flask import jsonify

import json

from app.core.extensions import docker
from app.modules.user.models import Permissions
from app.core.decorators import permission
from app.lib.common import bytes_to_human_readable

from . import api

@api.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.IMAGE_INFO)
def delete(id):
    response, status_code = docker.delete_image(id)
    return str(response), status_code

@api.route('/prune', methods=['POST'])
@permission(Permissions.IMAGE_DELETE)
def prune():
    filters = {"dangling": ["false"]}
    params = {"filters": json.dumps(filters)}
    response, status_code = docker.prune_images(params=params)

    images_deleted_list = response.json().get('ImagesDeleted')
    images_deleted = len(images_deleted_list) if images_deleted_list is not None else 0

    if images_deleted == 0:
        return jsonify({"message": "Nothing to prune"}), status_code

    space_reclaimed = bytes_to_human_readable(response.json().get('SpaceReclaimed', 0))
    
    message = f"Deleted {images_deleted} images, reclaimed {space_reclaimed}"
    
    return jsonify({"message": message}), status_code
