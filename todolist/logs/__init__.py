from flask import Blueprint, flash, redirect, url_for
from ..auth import login_manager, login_required, current_user
from .. import app
from datetime import date
from flask.json import JSONEncoder

logs = Blueprint('logs', __name__)

@logs.before_request
@login_required
def admin_access_check():
    if not current_user.is_authenticated:
        return login_manager.unauthorized()
    if not current_user.has_roles(('Supervisor','Admin', 'User')):
        flash('You have no access to this page')
        return redirect(url_for('home'))

#Views
from .logs_views import *

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat(' ')
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app.json_encoder = CustomJSONEncoder
