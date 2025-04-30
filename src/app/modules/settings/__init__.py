from flask import Blueprint, request
from flask_login import login_required

settings = Blueprint('settings', __name__, url_prefix='/settings', template_folder='templates', static_folder='static')

@settings.before_request
@login_required
def before_request():
    pass

@settings.context_processor
def inject_variables():
    active_page = str(request.blueprint).split('.')[-1]
    return dict(active_page=active_page)

from . import routes