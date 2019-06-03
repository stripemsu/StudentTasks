from flask import flash, redirect, url_for
from functools import wraps

from . import current_user, login_manager


def roles_required(*roles):
    """Decorator which specifies that a user must have __ANY__ of the specified roles.
    taken from flask security
    Example::
        @app.route('/dashboard')
        @roles_required('admin', 'editor')
        def dashboard():
            return 'Dashboard'
    The current user must have both the `admin` role and `editor` role in order
    to view the page.
    :param args: The required roles.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if ("ANY" not in roles):
                if not any(current_user.has_role(role) for role in roles):
                    flash('You have no access to this page')
                    return redirect(url_for('home'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

def role_required(role):
    """Decorator which specifies that a user must have all the specified roles.
    taken from flask security
    Example::
        @app.route('/dashboard')
        @roles_required('admin', 'editor')
        def dashboard():
            return 'Dashboard'
    The current user must have both the `admin` role and `editor` role in order
    to view the page.
    :param args: The required roles.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if ("ANY" not in role):
                if not current_user.has_role(role):
                    flash('You have no access to this page')
                    return redirect(url_for('home'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

