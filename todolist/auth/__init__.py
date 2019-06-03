from flask import Blueprint
from flask_login import  LoginManager, current_user, login_required
from .. import app

auth = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

from .decorators import roles_required, role_required
from .views import *
