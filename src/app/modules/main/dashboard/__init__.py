from flask import Blueprint

dashboard = Blueprint('dashboard', __name__, template_folder='templates', static_folder='static')

from . import routes