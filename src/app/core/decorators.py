from functools import wraps
from flask import render_template, jsonify, request
from flask_login import current_user

def permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission):
                message = f'You do not have the necessary permission.'
                code = 403
                if request.accept_mimetypes.best == 'application/json':
                    return jsonify({'error': 'Forbidden', 'message': message}), code
                else:
                    return render_template('error.html', message=message, code=code), code

            # Proceed to the view if access is granted
            return f(*args, **kwargs)
        return decorated_function
    return decorator
