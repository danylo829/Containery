from flask import Blueprint, request
from flask_login import login_required

user = Blueprint('user', __name__, url_prefix='/user', template_folder='templates', static_folder='static')

@user.before_request
@login_required
def before_request():
    pass

@user.context_processor
def inject_variables():
    active_page = str(request.blueprint).split('.')[-1]
    return dict(active_page=active_page)

from . import routes