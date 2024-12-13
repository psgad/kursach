from functools import wraps
from flask import redirect, url_for


def role_required(role, get_user):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_user()
            if user['role'] != role:
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
