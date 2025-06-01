from flask import render_template, jsonify

import json

from app.core.extensions import docker

import psutil

from . import dashboard

@dashboard.route('/', methods=['GET'])
def index():
    response, status_code = docker.info()
    info = []
    if status_code not in range(200, 300):
        message = response.text if hasattr(response, 'text') else str(response)
        try:
            message = json.loads(message).get('message', message)
        except json.JSONDecodeError:
            pass
        return render_template('error.html', message=message, code=status_code), status_code
    else:
        info = response.json()

    breadcrumbs = [
        {"name": "Dashboard", "url": None},
    ]
    page_title = "Dashboard"
    return render_template('dashboard.html', info=info, breadcrumbs=breadcrumbs, page_title=page_title)

@dashboard.route('/usage', methods=['GET'])
def get_usage():
    # CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)

    # RAM usage
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