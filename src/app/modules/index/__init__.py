from flask import Blueprint
from app.modules.user.models import User

index = Blueprint('index', __name__)

from . import routes