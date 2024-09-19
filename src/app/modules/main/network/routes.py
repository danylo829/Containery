from flask import Blueprint, render_template, url_for, jsonify
from flask_login import login_required

from app.utils.docker import Docker

network = Blueprint('network', __name__, template_folder='templates', static_folder='static')

@network.before_request
@login_required
def before_request():
    pass

@network.route('/list', methods=['GET'])
def get_list():
    response, status_code = Docker.get_networks()
    networks = []
    if status_code not in range(200, 300):
        flash(f'Error ({status_code}): {response.text}', 'error')
    else:
        networks = response.json()

    rows = []
    for network in networks:
        row = {
            'name': network['Name'],
            'driver': network['Driver'],
            'subnet': network['IPAM']['Config'][0]['Subnet'] if network['IPAM']['Config'] else 'N/A',
            'gateway': network['IPAM']['Config'][0]['Gateway'] if network['IPAM']['Config'] else 'N/A',
        }
        rows.append(row)

    rows = sorted(rows, key=lambda x: x['name'], reverse=True)

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Networks", "url": None},
    ]
    page_title = "Networks List"
    endpoint = "network"
    return render_template('network/table.html', rows=rows, breadcrumbs=breadcrumbs, page_title=page_title)