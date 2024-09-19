from flask import Blueprint, render_template, url_for, jsonify
from flask_login import login_required

from app.utils.docker import Docker

volume = Blueprint('volume', __name__, template_folder='templates', static_folder='app/modules/main/volume/static')

@volume.before_request
@login_required
def before_request():
    pass

@volume.route('/list', methods=['GET'])
def get_list():
    result, status = Docker.get_volumes()
    if status != 200:
        return jsonify(result), status

    volumes = result.get('Volumes', [])
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