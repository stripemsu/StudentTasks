from flask import request, render_template, flash, redirect
from .auth import current_user, login_required
from todolist import app


@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html')
