from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_assets import Environment

from app.lib.docker import Docker

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
socketio = SocketIO()
migrate = Migrate()
assets = Environment()
docker = Docker()