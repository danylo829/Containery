from flask import Blueprint, request, redirect, flash, url_for
from flask_login import login_required
from app.utils.docker import Docker

api = Blueprint('container', __name__)

@api.before_request
@login_required
def before_request():
    pass

@api.route('/<id>/restart', methods=['POST'])
def test(id):
    return Docker.restart_container(id=id)