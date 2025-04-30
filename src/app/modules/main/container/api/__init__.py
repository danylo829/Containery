from flask import Blueprint

api = Blueprint('container', __name__)

from . import routes