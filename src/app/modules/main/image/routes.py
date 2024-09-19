from flask import Blueprint, render_template, url_for, jsonify
from flask_login import login_required

from app.utils.docker import Docker
from app.utils.common import format_docker_timestamp

image = Blueprint('image', __name__, template_folder='templates', static_folder='static')

def image_info(id):
    result, status = Docker.inspect_image(id)
    if status != 200:
        return jsonify(result), status

    image_details = result

    general_info = {
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

    image_info = {
        'general_info': general_info,
        'env_vars': env_vars,
        'labels': labels,
        'repo_tags': repo_tags,
        'entrypoint': entrypoint,
        'cmd': cmd
    }

    return image_info

@image.before_request
@login_required
def before_request():
    pass

@image.route('/list', methods=['GET'])
def get_list():
    result, status = Docker.get_images()
    if status != 200:
        return jsonify(result), status

    images = result
    rows = []
    for image in images:
        row = {
            'id': image['Id'],
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
def info(id):
    image = image_info(id)
    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Images", "url": url_for('main.image.get_list')},
        {"name": image['repo_tags'][0].split(":")[0], "url": None},
    ]
    page_title = 'Image Details'
    
    return render_template('image/info.html', image=image, breadcrumbs=breadcrumbs, page_title=page_title)