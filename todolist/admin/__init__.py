from flask import Blueprint, flash, redirect, url_for
from ..auth import login_manager, login_required, current_user

admin = Blueprint('admin', __name__)

@admin.before_request
@login_required
def admin_access_check():
    if not current_user.is_authenticated:
        return login_manager.unauthorized()
    if not current_user.has_role('Admin'):
        flash('You have no access to this page')
        return redirect(url_for('home'))

from . import adm_views
