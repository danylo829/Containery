from flask import Blueprint, render_template, url_for, jsonify
from flask_login import login_required

from app.utils.docker import Docker
from app.utils.common import format_docker_timestamp

from app.decorators import permission
from app.models import Permissions

import json

network = Blueprint('network', __name__, template_folder='templates', static_folder='static')

docker = Docker()

def network_info(id):
    response, status_code = docker.inspect_network(id)
    network_details = []
    if status_code not in range(200, 300):
        return response, status_code
    else:
        network_details = response.json()

    # Extracting general network information
    network = {
        'Name': network_details["Name"],
        'Id': network_details["Id"],
        'Created': format_docker_timestamp(network_details["Created"]),
        'Scope': network_details["Scope"],
        'Driver': network_details["Driver"],
        'EnableIPv6': network_details["EnableIPv6"],
        'Internal': network_details["Internal"],
        'Attachable': network_details["Attachable"],
        'Ingress': network_details["Ingress"],
        'Containers': network_details.get("Containers", {}),
        'Labels': network_details.get("Labels", {}),
        'IPAM': [],  # Initialize IPAM as a list to hold configurations
    }
    
    subnets_gateways = []
    if 'IPAM' in network_details and network_details['IPAM']['Config']:
        for config in network_details['IPAM']['Config']:  # Loop through each config
            subnet = config.get('Subnet')
            gateway = config.get('Gateway')
            subnets_gateways.append((subnet, gateway))
    network['IPAM'] = subnets_gateways

    print(json.dumps(network, indent=4))  # Add this for debugging


    

    return network, 200

@network.before_request
@login_required
def before_request():
    pass

@network.route('/list', methods=['GET'])
@permission(Permissions.NETWORK_VIEW_LIST)
def get_list():
    response, status_code = docker.get_networks()
    networks = []
    if status_code not in range(200, 300):
        return render_template('error.html', message=response.text, code=status_code), status_code
    else:
        networks = response.json()

    rows = []
    for network in networks:
        row = {
            'id': network['Id'],
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

@network.route('/network/<id>', methods=['GET'])
@permission(Permissions.NETWORK_INFO)
def info(id):
    response, status_code = network_info(id)
    network = []
    if status_code not in range(200, 300):
        return render_template('error.html', message=response.text, code=status_code), status_code
    else:
        network = response

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Networks", "url": url_for('main.network.get_list')},
        {"name": network['Name'], "url": None},
    ]
    page_title = 'Network Details'
    
    return render_template('network/info.html', network=network, breadcrumbs=breadcrumbs, page_title=page_title)

@network.route('/<id>/delete', methods=['DELETE'])
@permission(Permissions.NETWORK_DELETE)
def delete(id):
    response, status_code = docker.delete_network(id)
    return str(response), status_code