from flask import Blueprint

module_name = __name__.split('.')[-1]
index = Blueprint(module_name, __name__)

from . import routes