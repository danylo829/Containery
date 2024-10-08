from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from enum import Enum
from time import time

db = SQLAlchemy()

class Role(Enum):
    ADMIN = 'administrator'
    DEVELOPER = 'developer'
    READER = 'reader'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default=Role.READER)
    created_at = db.Column(db.Integer, default=lambda: int(time()), nullable=False)
    
    personal_settings = db.relationship('PersonalSettings', backref='user', cascade="all, delete-orphan")

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
    def create_user(cls, username, password, role):
        if cls.query.filter_by(username=username).first():
            return "Username already exists"

        user = cls(username=username, password_hash=generate_password_hash(password), role=role)
        db.session.add(user)
        db.session.commit()

        # Set default personal settings
        for key, config in PersonalSettings.defaults.items():
            PersonalSettings.set_setting(user.id, key, config['default'])

    @classmethod
    def update_role(cls, id, new_role):
        user = cls.query.filter_by(id=id).first()
        if not user:
            return f"User not found"
        user.role = new_role
        db.session.commit()
            

    @classmethod
    def delete_user(cls, user_id):
        user = cls.query.get(user_id)
        if user and user_id != 1:
            db.session.delete(user)
            db.session.commit()
            return True
        return False

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
            'options': ['light', 'dark', 'dark_mixed', 'system'],
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