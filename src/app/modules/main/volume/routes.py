from flask import render_template, url_for

import json

from app.core.extensions import docker
from app.lib.common import format_docker_timestamp

from app.core.decorators import permission
from app.modules.user.models import Permissions

from . import volume

@volume.route('/list', methods=['GET'])
@permission(Permissions.VOLUME_VIEW_LIST)
def get_list():
    response, status_code = docker.get_volumes()
    volumes = []
    if status_code not in range(200, 300):
        message = response.text if hasattr(response, 'text') else str(response)
        try:
            message = json.loads(message).get('message', message)
        except json.JSONDecodeError:
            pass
        return render_template('error.html', message=message, code=status_code), status_code
    else:
        volumes = response.json().get('Volumes', [])

    rows = []
    for volume in volumes:
        row = {
            'name': volume['Name'],
            'mountpoint': volume['Mountpoint'],
        }
        rows.append(row)

    rows = sorted(rows, key=lambda x: x['name'], reverse=True)

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Volumes", "url": None},
    ]
    page_title = "Volumes List"
    return render_template('volume/table.html', rows=rows, breadcrumbs=breadcrumbs, page_title=page_title)

@volume.route('/<name>', methods=['GET'])
@permission(Permissions.VOLUME_INFO)
def info(name):
    response, status_code = docker.inspect_volume(name)
    volume = []
    if status_code not in range(200, 300):
        message = response.text if hasattr(response, 'text') else str(response)
        try:
            message = json.loads(message).get('message', message)
        except json.JSONDecodeError:
            pass
        return render_template('error.html', message=message, code=status_code), status_code
    else:
        volume = response.json()

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Volumes", "url": url_for('main.volume.get_list')},
        {"name": volume['Name'], "url": None},
    ]
    page_title = 'Volume Details'
    
    return render_template('volume/info.html', volume=volume, breadcrumbs=breadcrumbs, page_title=page_title, format_docker_timestamp=format_docker_timestamp)