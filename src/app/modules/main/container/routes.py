from flask import Blueprint, render_template, url_for, jsonify, flash, request, current_app
from flask_socketio import emit, join_room, leave_room
from flask_login import login_required

import json

from app.utils.docker import Docker
from app.utils.common import format_docker_timestamp

from app import socketio

container = Blueprint('container', __name__, template_folder='templates', static_folder='static')

from .api.routes import api

container.register_blueprint(api, url_prefix='/api')

docker = Docker()

def container_info (id):
    response, status_code = docker.inspect_container(id)
    container_details = []
    if status_code not in range(200, 300):
        return response, status_code
    else:
        container_details = response.json()

    general_info = {
        "id": container_details["Id"],
        "name": container_details["Name"].strip("/"),
        "status": container_details["State"]["Status"],
        "created_at": format_docker_timestamp(container_details['Created']),
        "restart_policy": container_details["HostConfig"]["RestartPolicy"]["Name"]
    }

    image = {
        "id": container_details["Image"],
        "name": container_details["Config"]["Image"]
    }

    env_vars = container_details["Config"].get("Env", [])

    labels = container_details["Config"].get("Labels", {})

    volumes = [mount["Source"] for mount in container_details.get("Mounts", [])]

    network_info = [
        {
            "network_name": network,
            "ip_address": details.get("IPAddress", ""),
            "exposed_ports": container_details["NetworkSettings"]["Ports"]
        }
        for network, details in container_details["NetworkSettings"]["Networks"].items()
    ]

    container_info = {
        'general_info': general_info,
        'image': image,
        'env_vars': env_vars,
        'labels': labels,
        'volumes': [{
            'host_path': mount['Source'],
            'container_path': mount['Destination']
        } for mount in container_details['Mounts']],
        'network_info': [{
            'network_name': net,
            'self_ip': network['IPAddress'],
            'exposed_ports': container_details['NetworkSettings']['Ports']
        } for net, network in container_details['NetworkSettings']['Networks'].items()]
    }

    return container_info, 200

def container_name (id):
    response, status_code = container_info(id)
    return response['general_info']['name'] if status_code in range(200, 300) else "Unknown Container"  # Fallback name

@container.before_request
@login_required
def before_request():
    pass

@container.route('/list', methods=['GET'])
def get_list():
    response, status_code = docker.get_containers()
    containers = []
    if status_code not in range(200, 300):
        flash(f'Error ({status_code}): {response.text}', 'error')
    else:
        containers = response.json()

    rows = []
    if containers is not None:
        for container in containers:
            row = {
                'id': container['Id'],
                'name': container['Names'][0].strip('/'),
                'status': container['Status'],
                'image': container['Image'],
                'imageID': container['ImageID']
            }
            rows.append(row)

    rows = sorted(rows, key=lambda x: x['name'], reverse=True)

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Containers", "url": None},
    ]
    page_title = "Container List"
    endpoint = "container"

    return render_template('container/table.html', rows=rows, breadcrumbs=breadcrumbs, page_title=page_title)

@container.route('/<id>', methods=['GET'])
def info(id): 
    response, status_code = container_info(id)
    container = []
    if status_code not in range(200, 300):
        flash(f'Error ({status_code}): {response.text}', 'error')
    else:
        container = response

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Containers", "url": url_for('main.container.get_list')},
        {"name": container_name(id), "url": None},
    ]
    page_title = 'Container Details'
    
    return render_template('container/info.html', container=container, breadcrumbs=breadcrumbs, page_title=page_title)


@container.route('/<id>/logs', methods=['GET'])
def logs(id):
    response, status_code = docker.get_logs(id)
    logs = []
    if status_code not in range(200, 300):
        flash(f'Error ({status_code}): {response.text}', 'error')
    else:
        logs = response

    log_text = ''.join(log['message'] for log in logs)
    
    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Containers", "url": url_for('main.container.get_list')},
        {"name": container_name(id), "url": url_for('main.container.info', id=id)},
        {"name": "Logs", "url": None},
    ]
    page_title = 'Container Logs'
    
    return render_template('container/logs.html', log_text=log_text, breadcrumbs=breadcrumbs, page_title=page_title)


@container.route('/<id>/processes', methods=['GET'])
def processes(id):
    response, status_code = docker.get_processes(id)
    processes = []
    if status_code not in range(200, 300):
        # Custom error messages
        if status_code == 409:
            id = response.json()['message'].split(' ')[1]
            name = container_name(id)
            flash(f'Container {name} is not running', 'error')
        # Default error message
        else:
            flash(f'Error ({status_code}): {response.text}', 'error')
    else:
        processes = response.json()

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Containers", "url": url_for('main.container.get_list')},
        {"name": container_name(id), "url": url_for('main.container.info', id=id)},
        {"name": "Processes", "url": None},
    ]
    page_title = f'{container_name(id)} processes'
    
    return render_template('container/processes.html', processes=processes, breadcrumbs=breadcrumbs, page_title=page_title)

@container.route('/<id>/terminal', methods=['GET'])
def console(id):
    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Containers", "url": url_for('main.container.get_list')},
        {"name": container_name(id), "url": url_for('main.container.info', id=id)},
        {"name": "Terminal", "url": None},
    ]
    page_title = 'Container terminal'
    
    return render_template('container/terminal.html', container_id=id, breadcrumbs=breadcrumbs, page_title=page_title)

@socketio.on('start_session')
def handle_start_session(data):
    container_id = data['container_id']
    cmd = data['command'].split()
    user = data['user']
    sid = request.sid  # Using flask.request for session ID

    exec_create_endpoint = f"/containers/{container_id}/exec"
    payload = {"AttachStdin": True, "AttachStdout": True, "AttachStderr": True, "Tty": True, "Cmd": cmd, "User": user}

    exec_id = docker.create_exec(exec_create_endpoint, payload=payload)

    if exec_id == None:
        emit('output', {'data': 'Could not create exec session. Check if container is running.\r\n'})
        return

    socketio.start_background_task(target=docker.start_exec_session, exec_id=exec_id, sid=sid, socketio=socketio, app=current_app._get_current_object())

@socketio.on('input')
def handle_command(data):
    command = data['command']
    sid = request.sid  # Using flask.request for session ID

    response = docker.handle_command(command, sid)
    if response:
        emit('output', {'data': response})
