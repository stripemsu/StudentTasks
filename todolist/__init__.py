from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('../config.py')

from todolist.database import db, User, refill_db
from todolist.views import home

db.init_app(app)

app.secret_key = 'vhd89kb5upC6J3nPOtf1LVtE' #Random key

from .auth import auth
app.register_blueprint(auth)
from .tasks import tasks
app.register_blueprint(tasks)
from .admin import admin
app.register_blueprint(admin)
from .logs import logs
app.register_blueprint(logs)


#check if db's created inside
with app.app_context():
    refill_db()
