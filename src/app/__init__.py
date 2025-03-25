from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_socketio import SocketIO
from .models import db, Permissions, User, PersonalSettings, GlobalSettings
from flask_migrate import Migrate
from flask_assets import Environment, Bundle

import app.utils.common as utils
from app.utils.docker import Docker
from werkzeug.debug import DebuggedApplication

socketio = SocketIO()
migrate = Migrate()
assets = Environment()
docker = Docker()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    socketio.init_app(app)

    docker.init_app(app)

    csrf = CSRFProtect()
    csrf.init_app(app)

    assets.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject():
        return dict(PersonalSettings=PersonalSettings, GlobalSettings=GlobalSettings, Permissions=Permissions, utils=utils)

    db.init_app(app)
    migrate.init_app(app, db)

    app_css = Bundle(
        "styles/common.css",
        "styles/colors.css",
        "styles/base.css",
        "styles/modal.css",
        "styles/icons.css",
        filters="rcssmin",
        output="dist/css/app.%(version)s.css"
    )

    app_js = Bundle(
        "js/base.js",
        "js/modal.js",
        "js/table.js",
        "js/scrollbar.js",
        filters='rjsmin',
        output="dist/js/app.%(version)s.js",
    )

    assets.register("app_css", app_css)
    assets.register("app_js", app_js)

    from .index import index
    from .modules.main import main
    from .modules.auth.routes import auth
    from .modules.user.routes import user
    from .modules.settings.routes import settings
    
    app.register_blueprint(index)
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(settings)

    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True, pin_security=False)
    
    return app
