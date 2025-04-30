from flask import Blueprint

api = Blueprint('network', __name__)

from . import routes