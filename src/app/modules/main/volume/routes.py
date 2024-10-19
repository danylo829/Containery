from flask import Blueprint, render_template, url_for, jsonify, flash
from flask_login import login_required

from app.utils.docker import Docker

from app.decorators import permission
from app.models import Permissions

volume = Blueprint('volume', __name__, template_folder='templates', static_folder='app/modules/main/volume/static')

docker = Docker()

@volume.before_request
@login_required
def before_request():
    pass

@volume.route('/list', methods=['GET'])
@permission(Permissions.VOLUME_VIEW_LIST)
def get_list():
    response, status_code = docker.get_volumes()
    volumes = []
    if status_code not in range(200, 300):
        return render_template('error.html', message=response.text, code=status_code), status_code
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
    endpoint = "volume"
    return render_template('volume/table.html', rows=rows, breadcrumbs=breadcrumbs, page_title=page_title)