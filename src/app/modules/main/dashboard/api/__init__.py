from flask import Blueprint

api = Blueprint('dashboard', __name__)

from . import routes