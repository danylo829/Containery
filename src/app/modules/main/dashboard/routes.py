from flask import Blueprint, redirect, url_for, render_template, jsonify, flash
from flask_login import login_required

from app.utils.docker import Docker

import psutil

dashboard = Blueprint('dashboard', __name__, template_folder='templates', static_folder='static')

docker = Docker()

@dashboard.before_request
@login_required
def before_request():
    pass

@dashboard.route('/', methods=['GET'])
def index():
    response, status_code = docker.info()
    info = []
    if status_code not in range(200, 300):
        return render_template('error.html', message=response.text, code=status_code), status_code
    else:
        info = response.json()

    breadcrumbs = [
        {"name": "Dashboard", "url": None},
    ]
    page_title = "Dashboard"
    return render_template('dashboard.html', info=info, breadcrumbs=breadcrumbs, page_title=page_title)

@dashboard.route('/usage', methods=['GET'])
def get_usage():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage_percent = psutil.virtual_memory().percent
    ram_usage_absolute = round((psutil.virtual_memory().used / 1024 / 1024 / 1024), 2)
    ram_total = round((psutil.virtual_memory().total / 1024 / 1024 / 1024), 2)
    return jsonify(cpu=cpu_usage, ram_percent=ram_usage_percent, ram_absolute=ram_usage_absolute, ram_total=ram_total)