from flask import Blueprint, render_template, url_for, request, current_app

from app.models import Permissions
from app.decorators import permission
from app.utils.common import format_docker_timestamp, format_unix_timestamp

from app import docker

image = Blueprint('image', __name__, template_folder='templates', static_folder='static')

from .api.routes import api

image.register_blueprint(api, url_prefix='/api')

def image_info(id):
    response, status_code = docker.inspect_image(id)
    image_details = []
    if status_code not in range(200, 300):
        return response, status_code
    else:
        image_details = response.json()

    general_info = {
        "id": id,
        "architecture": image_details["Architecture"],
        "docker_version": image_details["DockerVersion"],
        "os": image_details["Os"],
        "created_at": format_docker_timestamp(image_details["Created"]),
        "size": round(image_details["Size"] / 1024 / 1024, 2),
        "author": image_details.get("Author", ""),
        "comment": image_details.get("Comment", "")
    }

    env_vars = image_details["Config"].get("Env", [])

    labels = image_details["Config"].get("Labels", {})

    repo_tags = image_details.get("RepoTags", [])
    
    entrypoint = image_details["Config"].get("Entrypoint", [])
    
    cmd = image_details["Config"].get("Cmd", [])

    image = {
        'general_info': general_info,
        'env_vars': env_vars,
        'labels': labels,
        'repo_tags': repo_tags,
        'entrypoint': entrypoint,
        'cmd': cmd
    }

    return image, 200

def image_name(id):
    response, status_code = image_info(id)
    return response['repo_tags'][0] if 'repo_tags' in response and response['repo_tags'] and status_code in range(200, 300) else "Unamed Image"

@image.context_processor
def inject_variables():
    active_page = str(request.blueprint).split('.')[-1]
    return dict(active_page=active_page)

@image.route('/list', methods=['GET'])
@permission(Permissions.IMAGE_VIEW_LIST)
def get_list():
    response, status_code = docker.get_images()
    images = []
    if status_code not in range(200, 300):
        message = response.text if hasattr(response, 'text') else str(response)
        return render_template('error.html', message=message, code=status_code), status_code
    else:
        images = response.json()

    rows = []
    for image in images:
        row = {
            'id': image['Id'],
            'created': format_unix_timestamp(image['Created']),
            'repo_tags': ', '.join(image['RepoTags']) if image.get('RepoTags') else 'N/A',
            'size': round(image['Size'] / 1024 / 1024, 2)
        }
        rows.append(row)

    rows = sorted(rows, key=lambda x: x['repo_tags'], reverse=True)

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Images", "url": None},
    ]
    page_title = "Images List"
    endpoint = "image"
    return render_template('image/table.html', rows=rows, breadcrumbs=breadcrumbs, page_title=page_title)

@image.route('/<id>', methods=['GET'])
@permission(Permissions.IMAGE_INFO)
def info(id):
    response, status_code = image_info(id)
    image = []
    if status_code not in range(200, 300):
        message = response.text if hasattr(response, 'text') else str(response)
        return render_template('error.html', message=message, code=status_code), status_code
    else:
        image = response

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Images", "url": url_for('main.image.get_list')},
        {"name": image_name(id), "url": None},
    ]
    page_title = 'Image Details'
    
    return render_template('image/info.html', image=image, breadcrumbs=breadcrumbs, page_title=page_title)