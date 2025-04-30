from flask import Blueprint

api = Blueprint('volume', __name__)

from . import routes