from flask import Blueprint, render_template, jsonify, current_app
from flask_login import login_required

from app import docker

import psutil

dashboard = Blueprint('dashboard', __name__, template_folder='templates', static_folder='static')

@dashboard.before_request
@login_required
def before_request():
    pass

@dashboard.route('/', methods=['GET'])
def index():
    response, status_code = docker.info()
    info = []
    if status_code not in range(200, 300):
        message = response.text if hasattr(response, 'text') else str(response)
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

    io_stats = psutil.disk_io_counters()
    io_read_bytes = round(io_stats.read_bytes / 1024, 2)  # Convert to GB
    io_write_bytes = round(io_stats.write_bytes / 1024, 2)  # Convert to GB

    return jsonify(
        cpu=cpu_usage,
        ram_percent=ram_usage_percent,
        ram_absolute=ram_usage_absolute,
        ram_total=ram_total,
        load_average=load_average,
        io_read_bytes=io_read_bytes,
        io_write_bytes=io_write_bytes
    )