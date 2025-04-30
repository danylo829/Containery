from flask import Blueprint

index = Blueprint('index', __name__)

from . import routes