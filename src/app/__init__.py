from flask import Flask

from flask_assets import Bundle
from werkzeug.debug import DebuggedApplication

import app.utils.common as utils
import app.extensions as extensions

from app.modules.user.models import Permissions, User, PersonalSettings
from app.modules.settings.models import GlobalSettings

from app.index import index
from app.modules.main import main
from app.modules.auth.routes import auth
from app.modules.user.routes import user
from app.modules.settings.routes import settings

class ApplicationFactory:
    def __init__(self):
        self.db = extensions.db
        self.csrf = extensions.csrf
        self.login_manager = extensions.login_manager
        self.socketio = extensions.socketio
        self.migrate = extensions.migrate
        self.assets = extensions.assets
        self.docker = extensions.docker

    def configure_extensions(self, app):
        """Configure Flask extensions."""
        self.db.init_app(app)
        self.migrate.init_app(app, self.db)
        self.socketio.init_app(app)
        self.docker.init_app(app)
        self.csrf.init_app(app)
        self.assets.init_app(app)

        self.login_manager.init_app(app)
        self.login_manager.login_view = 'auth.login'

    def register_blueprints(self, app):
        """Register application blueprints."""
        blueprints = [index, main, auth, user, settings]
        for blueprint in blueprints:
            app.register_blueprint(blueprint)

    def configure_assets(self):
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

    def create_app(self):
        """
        Create and configure the Flask application.
        
        :return: Configured Flask application
        """
        app = Flask(__name__)
        
        app.config.from_object('app.config.Config')

        self.configure_extensions(app)
        self.configure_assets()
        self.configure_context_processors(app)
        self.configure_user_loader()
        self.register_blueprints(app)

        if app.debug:
            app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True, pin_security=False)
        
        return app