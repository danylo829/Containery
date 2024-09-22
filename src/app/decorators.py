from functools import wraps
from flask import flash, redirect, url_for, render_template, jsonify, request
from flask_login import current_user
from app.models import Role

def role(roles, allow=True):
    """
    A decorator that either allows or denies access based on roles, with different handling for API and HTML routes.

    :param roles: List of roles to allow or deny.
    :param allow: If True, allows the roles listed. If False, denies the roles listed.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = current_user.role

            is_api_request = request.accept_mimetypes.best == 'application/json'
            
            role_check = user_role in [role.value for role in roles]
            
            message = 'You do not have the necessary permissions.'
            code = 403
            if (allow and not role_check) or (not allow and role_check):
                if is_api_request:
                    return jsonify({'error': 'Forbidden', 'message': message}), code
                else:
                    return render_template('error.html', message=message, code=code), code

            # Proceed to the view if access is granted
            return f(*args, **kwargs)
        return decorated_function
    return decorator
