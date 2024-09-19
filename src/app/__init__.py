from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO
from .models import db, init_db, User, PersonalSettings, GlobalSettings

import app.utils.common as utils

from werkzeug.debug import DebuggedApplication

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    socketio.init_app(app)

    csrf = CSRFProtect()
    csrf.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject():
        return dict(PersonalSettings=PersonalSettings, GlobalSettings=GlobalSettings, utils=utils)

    db.init_app(app)
    with app.app_context():
        init_db()

    from .index import index
    from .modules.main import main
    from .modules.auth.routes import auth
    from .modules.user.routes import user
    
    app.register_blueprint(index)
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(user)

    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True, pin_security=False)
    
    return app
