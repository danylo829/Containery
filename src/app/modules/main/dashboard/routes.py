from flask import render_template, jsonify, session

import json
import psutil

from app.core.extensions import docker

from app.config import Config

import app.modules.main.dashboard.utils as utils
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

    latest_version, show_update_notification = utils.check_for_update()

    page_title = "Dashboard"
    return render_template(
        'dashboard.html',
        info=info,
        page_title=page_title,
        show_update_notification=show_update_notification,
        latest_version=latest_version,
        installed_version=Config.VERSION
    )

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

@dashboard.route('/dismiss-update-notification', methods=['POST'])
def dismiss_update_notification():
    session['dismiss_update_notification'] = True
    return jsonify({'success': True}), 200