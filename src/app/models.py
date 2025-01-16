from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from enum import IntEnum, Enum
from hashlib import sha256
from time import time

db = SQLAlchemy()

def stable_hash(value):
    return int(sha256(value.encode()).hexdigest(), 16) % (10**8)  # Limit the size of the hash

permission_names = [
    'USER_ADD',
    'USER_DELETE',
    'USER_EDIT',
    'USER_VIEW_LIST',
    'USER_VIEW_PROFILE',
    
    'ROLE_ADD',
    'ROLE_VIEW',
    'ROLE_VIEW_LIST',
    'ROLE_EDIT',
    
    'CONTAINER_INFO',
    'CONTAINER_START',
    'CONTAINER_STOP',
    'CONTAINER_RESTART',
    'CONTAINER_DELETE',
    'CONTAINER_VIEW_LIST',
    'CONTAINER_EXEC',
    
    'IMAGE_INFO',
    'IMAGE_DELETE',
    'IMAGE_VIEW_LIST',
    
    'VOLUME_INFO',
    'VOLUME_DELETE',
    'VOLUME_VIEW_LIST',
    
    'NETWORK_INFO',
    'NETWORK_DELETE',
    'NETWORK_VIEW_LIST',
    
    'GLOBAL_SETTINGS_VIEW',
    'GLOBAL_SETTINGS_EDIT'
]

Permissions = IntEnum('Permissions', {name: stable_hash(name) for name in permission_names})

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.Integer, default=lambda: int(time()), nullable=False)

    user_roles = db.relationship('UserRole', back_populates='role', cascade='all, delete-orphan')
    permissions = db.relationship('RolePermission', back_populates='role', cascade='all, delete-orphan')

    @classmethod
    def create_role(cls, name):
        if not name or not name.strip():
            raise ValueError("Role name cannot be empty.")

        if len(name) > 20:
            raise ValueError("Role name must be 20 characters or less.")

        existing_role = cls.query.filter_by(name=name).first()
        if existing_role:
            raise ValueError(f"Role '{name}' already exists.")

        try:
            role = cls(name=name)
            db.session.add(role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to create role: {str(e)}")

        return role
    
    @classmethod
    def delete_role(cls, id):
        """Deletes a role by its ID."""
        
        if not isinstance(id, int) or id <= 0:
            raise ValueError("Invalid role ID provided.")

        if id == 1:
            raise PermissionError("The admin role cannot be deleted.")

        role = cls.query.filter_by(id=id).first()

        if not role:
            raise LookupError(f"Role with ID '{id}' not found.")

        try:
            db.session.delete(role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to delete role: {str(e)}")


    def rename(self, name):
        if not name or not isinstance(name, str):
            raise ValueError("Invalid role name")

        self.name = name
        db.session.commit()

    def get_user_count(self):
        """Returns the number of users assigned to this role."""
        if not self.id:
            raise ValueError("The role must have a valid ID.")

        user_count = UserRole.query.filter_by(role_id=self.id).count()

        return user_count

    def get_permissions(self):
        return RolePermission.query.filter_by(role_id=self.id).all()

    def get_permissions_values(self):
        return [rp.permission for rp in RolePermission.query.filter_by(role_id=self.id).all()]

    @classmethod
    def get_roles(cls):
        return cls.query.all()

    @classmethod
    def get_role(cls, id):
        if not isinstance(id, int) or id <= 0:
            raise ValueError("Invalid role ID provided.")
        
        role = cls.query.filter_by(id=id).first()

        if not role:
            raise LookupError(f"Role with ID '{id}' not found.")

        return role


    def add_permission(self, permission):
        if not isinstance(permission, Permissions):
            raise ValueError("Permission must be an instance of Permissions Enum.")

        if any(rp.permission == permission.value for rp in self.permissions):
            raise ValueError(f"Permission '{permission.name}' is already assigned to role '{self.name}'.")

        new_permission = RolePermission(role_id=self.id, permission=permission.value)
        db.session.add(new_permission)
        db.session.commit()

    def remove_permission(self, permission):
        if not isinstance(permission, Permissions):
            raise ValueError("Permission must be an instance of Permissions Enum.")

        role_permission = RolePermission.query.filter_by(role_id=self.id, permission=permission.value).first()
        if not role_permission:
            raise ValueError(f"Permission '{permission.name}' not found for role '{self.name}'.")

        db.session.delete(role_permission)
        db.session.commit()

class RolePermission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    permission = db.Column(db.Integer, nullable=False)
    
    role = db.relationship('Role', back_populates='permissions')

class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    user = db.relationship('User', back_populates='user_roles')
    role = db.relationship('Role', back_populates='user_roles')

class User(UserMixin, db.Model):
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
        """Check if the user has a specific permission through any of their roles."""
        if not isinstance(permission, Permissions):
            raise ValueError("Permission must be an instance of Permissions Enum.")

        for user_role in self.user_roles:
            # Check if super admin
            if user_role.role_id == 1:
                return True

            for role_permission in user_role.role.permissions:
                if role_permission.permission == permission.value:
                    return True

        return False

    def get_roles(self):
        return [user_role.role for user_role in self.user_roles]

    def get_roles_str(self):
        return ', '.join([role.role.name for role in self.user_roles])

    def assign_role(self, role):
        """Assigns a role to the user."""
        
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
        """Removes a role from the user, with an additional check to prevent removing the admin role from the main admin."""
        
        if not isinstance(role, Role):
            raise ValueError(f"Expected a Role instance, got {type(role)}")

        if self.id == 1 and role.id == 1:
            raise PermissionError("Cannot remove the 'admin' role from the main admin.")

        # Check if the user has the role to be removed
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

class GlobalSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(150), unique=True, nullable=False)
    value = db.Column(db.String(150), nullable=False)

    defaults = {
        'docker_socket': '/var/run/docker.sock',
        'theme_color': '#2196F3',
        'dashboard_refresh_interval': 5,
        'log_retention_days': 30,
        'session_timeout': 1800,
        'password_min_length': 8,
    }

    @classmethod
    def get_setting(cls, key):
        if key not in cls.defaults:
            raise KeyError(f"The setting '{key}' is not defined in defaults.")

        try:
            setting = cls.query.filter_by(key=key).first()
            return setting.value if setting else cls.defaults[key]
        except Exception as e:
            raise RuntimeError(f"Database error while retrieving setting '{key}': {str(e)}")

    @classmethod
    def set_setting(cls, key, value):
        if key not in cls.defaults:
            raise KeyError(f"The setting '{key}' is not defined in defaults.")

        if key == 'dashboard_refresh_interval' or key == 'log_retention_days' or key == 'session_timeout':
            try:
                value = int(value)
                if value <= 0:
                    raise ValueError(f"The value for '{key}' must be a positive integer.")
            except ValueError:
                raise ValueError(f"The value for '{key}' must be an integer.")

        try:
            setting = cls.query.filter_by(key=key).first()
            if setting:
                setting.value = str(value)
            else:
                setting = cls(key=key, value=str(value))
                db.session.add(setting)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Database error while setting '{key}': {str(e)}")

    @classmethod
    def delete_setting(cls, key):
        if key not in cls.defaults:
            raise KeyError(f"The setting '{key}' is not defined in defaults.")
        
        try:
            setting = cls.query.filter_by(key=key).first()
            if setting:
                db.session.delete(setting)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Database error while deleting setting '{key}': {str(e)}")

class PersonalSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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