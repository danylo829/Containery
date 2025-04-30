from flask import Blueprint

api = Blueprint('image', __name__)

from . import routes