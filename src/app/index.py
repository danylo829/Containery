from flask import Blueprint, redirect, url_for, session
from app.models import User

index = Blueprint('index', __name__)

@index.route('/', methods=['GET'])
def root():
    if User.query.first():
        return redirect(url_for('auth.login'))
    return redirect(url_for('auth.install'))

@index.route('/toggle_sidebar', methods=['POST'])
def toggle_sidebar():
    if session.get('sidebar_state') == 'closed':
        session['sidebar_state'] = 'open'
    else:
        session['sidebar_state'] = 'closed'
    
    return '', 204