import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_assets import Environment, Bundle
from werkzeug.debug import DebuggedApplication

import app.utils.common as utils

from app.models import db, Permissions, User, PersonalSettings, GlobalSettings
from app.utils.docker import Docker

csrf = CSRFProtect()
login_manager = LoginManager()
socketio = SocketIO()
migrate = Migrate()
assets = Environment()
docker = Docker()

class ApplicationFactory:
    def __init__(self):
        self.csrf = csrf
        self.login_manager = login_manager
        self.socketio = socketio
        self.migrate = migrate
        self.assets = assets
        self.docker = docker

    def configure_extensions(self, app):
        """Configure Flask extensions."""
        self.socketio.init_app(app)
        self.docker.init_app(app)
        self.csrf.init_app(app)
        self.assets.init_app(app)

        self.login_manager.init_app(app)
        self.login_manager.login_view = 'auth.login'

        db.init_app(app)
        self.migrate.init_app(app, db)

    def register_blueprints(self, app):
        """Register application blueprints."""
        from .index import index
        from .modules.main import main
        from .modules.auth.routes import auth
        from .modules.user.routes import user
        from .modules.settings.routes import settings
        
        blueprints = [index, main, auth, user, settings]
        for blueprint in blueprints:
            app.register_blueprint(blueprint)

    def configure_assets(self, app):
        """Configure and register asset bundles."""
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

        self.assets.register("app_css", app_css)
        self.assets.register("app_js", app_js)

    def configure_context_processors(self, app):
        """Add context processors to the application."""
        @app.context_processor
        def inject_context():
            return dict(
                PersonalSettings=PersonalSettings, 
                GlobalSettings=GlobalSettings, 
                Permissions=Permissions, 
                utils=utils
            )

    def configure_user_loader(self):
        """Configure the user loader for Flask-Login."""
        @self.login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    def create_app(self, config_object='app.config.Config'):
        """
        Create and configure the Flask application.
        
        :param config_object: Path to the configuration object
        :return: Configured Flask application
        """
        app = Flask(__name__)
        
        app.config.from_object(config_object)

        self.configure_extensions(app)
        self.configure_assets(app)
        self.configure_context_processors(app)
        self.configure_user_loader()
        self.register_blueprints(app)

        if app.debug:
            app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True, pin_security=False)
        
        return app