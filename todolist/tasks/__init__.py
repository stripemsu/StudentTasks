from flask import Blueprint, flash, redirect, url_for
from ..auth import login_manager, login_required, current_user
from werkzeug import SharedDataMiddleware
from .. import app

tasks = Blueprint('tasks', __name__)
app.add_url_rule('/images/<filename>', 'image_files',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/images':  app.config['IMAGE_FOLDER']
})

@tasks.before_request
@login_required
def admin_access_check():
    if not current_user.is_authenticated:
        return login_manager.unauthorized()
#    if not current_user.has_roles('User'):
#        flash('You have no access to this page')
#        return redirect(url_for('home'))

#Views
from .task_views import *
from .task_admviews import *
