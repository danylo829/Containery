from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from time import time

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.Integer, default=lambda: int(time()), nullable=False)
    
    personal_settings = db.relationship('PersonalSettings', backref='user', uselist=False, cascade="all, delete-orphan")

    @classmethod
    def update_password(cls, username, new_password):
        user = cls.query.filter_by(username=username).first()
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

    @classmethod
    def check_password(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        return user and check_password_hash(user.password_hash, password)

    @classmethod
    def create_user(cls, username, password):
        if cls.query.filter_by(username=username).first():
            return ("danger", "Username already exists")

        user = cls(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

        # Set default personal settings
        for key, config in PersonalSettings.defaults.items():
            PersonalSettings.set_setting(user.id, key, config['default'])

class GlobalSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(150), unique=True, nullable=False)
    setting_value = db.Column(db.String(150), nullable=False)

    defaults = {
        'docker_socket': {
            'default': '/var/run/docker.sock'
        }
    }

    @classmethod
    def get_setting(cls, key):
        setting = cls.query.filter_by(setting_key=key).first()
        return setting.setting_value if setting else None

    @classmethod
    def set_setting(cls, key, value):
        setting = cls.query.filter_by(setting_key=key).first()
        if setting:
            setting.setting_value = value
        else:
            setting = cls(setting_key=key, setting_value=value)
            db.session.add(setting)

        db.session.commit()


class PersonalSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    setting_key = db.Column(db.String(150), nullable=False)
    setting_value = db.Column(db.String(150), nullable=False)

    defaults = {
        'constrain_tables_view': {
            'default': False,
        },
        'theme': {
            'options': ['light', 'dark', 'system'],
            'default': 'system',
        },
    }

    @classmethod
    def get_setting(cls, user_id, key):
        setting = cls.query.filter_by(user_id=user_id, setting_key=key).first()
        return setting.setting_value if setting else None

    @classmethod
    def set_setting(cls, user_id, key, value):
        setting = cls.query.filter_by(user_id=user_id, setting_key=key).first()
        if setting:
            setting.setting_value = value
        else:
            setting = cls(user_id=user_id, setting_key=key, setting_value=value)
            db.session.add(setting)
        
        db.session.commit()

def init_db():
    db.create_all()
