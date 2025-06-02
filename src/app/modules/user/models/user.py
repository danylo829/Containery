from app.core.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
from .role import Role, UserRole

class User(UserMixin, db.Model):
    __tablename__ = 'usr_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.Integer, default=lambda: int(time()), nullable=False)

    personal_settings = db.relationship('PersonalSettings', backref='user', cascade="all, delete-orphan")
    user_roles = db.relationship('UserRole', back_populates='user', cascade='all, delete-orphan')

    def update_password(self, new_password):
        self.password_hash = generate_password_hash(new_password)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create_user(cls, username, password):
        if cls.query.filter_by(username=username).first():
            return "Username already exists"

        user = cls(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

        # Set default personal settings
        for key, config in PersonalSettings.defaults.items():
            PersonalSettings.set_setting(user.id, key, config['default'])
        
        return user

    def has_permission(self, permission):
        if not isinstance(permission, int):
            raise ValueError("Permission must be an integer value from Permissions.")
        for user_role in self.user_roles:
            if user_role.role_id == 1:
                return True
            for role_permission in user_role.role.permissions:
                if role_permission.permission == permission:
                    return True
        return False

    def get_roles(self):
        return [user_role.role for user_role in self.user_roles]

    def get_roles_str(self):
        return ', '.join([role.role.name for role in self.user_roles])

    def assign_role(self, role):
        if not isinstance(role, Role):
            raise ValueError("Role must be an instance of the Role model.")
        if not role:
            raise LookupError("The role provided does not exist.")
        if any(user_role.role_id == role.id for user_role in self.user_roles):
            raise ValueError(f"Role '{role.name}' is already assigned to the user.")
        new_user_role = UserRole(user_id=self.id, role_id=role.id)
        db.session.add(new_user_role)
        db.session.commit()

    def remove_role(self, role):
        if not isinstance(role, Role):
            raise ValueError(f"Expected a Role instance, got {type(role)}")
        if self.id == 1 and role.id == 1:
            raise PermissionError("Cannot remove the 'admin' role from the main admin.")
        user_role = UserRole.query.filter_by(user_id=self.id, role_id=role.id).first()
        if not user_role:
            raise LookupError(f"Role '{role.name}' not assigned to the user.")
        try:
            db.session.delete(user_role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to remove role: {str(e)}")

    @classmethod
    def delete_user(cls, id):    
        if not isinstance(id, int) or id <= 0:
            raise ValueError("Invalid user ID provided.")
        if id == 1:
            raise PermissionError("The admin user cannot be deleted.")
        user = cls.query.filter_by(id=id).first()
        if not user:
            raise LookupError(f"User with ID '{id}' not found.")
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to delete user: {str(e)}")

class PersonalSettings(db.Model):
    __tablename__ = 'usr_personal_settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usr_user.id'), nullable=False)
    key = db.Column(db.String(150), nullable=False)
    value = db.Column(db.String(150), nullable=False)

    defaults = {
        'theme': {
            'options': ['light', 'dark', 'dark_mixed', 'system'],
            'default': 'system',
        },
    }

    @classmethod
    def get_setting(cls, user_id, key):
        setting = cls.query.filter_by(user_id=user_id, key=key).first()
        return setting.value if setting else None

    @classmethod
    def set_setting(cls, user_id, key, value):
        setting = cls.query.filter_by(user_id=user_id, key=key).first()
        if setting:
            setting.value = value
        else:
            setting = cls(user_id=user_id, key=key, value=value)
            db.session.add(setting)
        db.session.commit()
