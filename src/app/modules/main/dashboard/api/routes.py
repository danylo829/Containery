from flask import jsonify, session

from app.core.extensions import docker
from app.lib.common import bytes_to_human_readable

import psutil
import json

from . import api

@api.route('/usage', methods=['GET'])
def get_usage():
    cpu_usage = psutil.cpu_percent(interval=1)

    ram_usage_percent = psutil.virtual_memory().percent
    ram_usage_absolute = round((psutil.virtual_memory().used / 1024 / 1024 / 1024), 2)
    ram_total = round((psutil.virtual_memory().total / 1024 / 1024 / 1024), 2)

    # Load average
    load_average = psutil.getloadavg()  # Returns a tuple (1min, 5min, 15min)

    return jsonify(
        cpu=cpu_usage,
        ram_percent=ram_usage_percent,
        ram_absolute=ram_usage_absolute,
        ram_total=ram_total,
        load_average=load_average
    )

@api.route('/dismiss-update-notification', methods=['POST'])
def dismiss_update_notification():
    session['dismiss_update_notification'] = True
    return jsonify({'success': True}), 200

@api.route('/prune', methods=['POST'])
def prune():
    reclaimed_space = 0

    response, status_code = docker.prune_containers()
    if status_code not in range(200, 300):
        return jsonify({'message': 'Failed to prune containers'}), status_code
    reclaimed_space += response.json().get('SpaceReclaimed', 0)

    filters = {"dangling": ["false"]}
    params = {"filters": json.dumps(filters)}
    response, status_code = docker.prune_images(params=params)
    if status_code not in range(200, 300):
        return jsonify({'message': 'Failed to prune images'}), status_code
    reclaimed_space += response.json().get('SpaceReclaimed', 0)

    response, status_code = docker.prune_volumes()
    if status_code not in range(200, 300):
        return jsonify({'message': 'Failed to prune volumes'}), status_code
    reclaimed_space += response.json().get('SpaceReclaimed', 0)

    response, status_code = docker.prune_networks()
    if status_code not in range(200, 300):
        return jsonify({'message': 'Failed to prune networks'}), status_code
    reclaimed_space += response.json().get('SpaceReclaimed', 0)

    response, status_code = docker.prune_build_cache()
    if status_code not in range(200, 300):
        return jsonify({'message': 'Failed to prune build cache'}), status_code
    reclaimed_space += response.json().get('SpaceReclaimed', 0)

    message = f"Reclaimed {bytes_to_human_readable(reclaimed_space)} of disk space."

    return jsonify({'message': message}), 200