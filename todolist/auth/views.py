from .. import db
from ..database import User
from flask import request, render_template, flash, redirect, url_for, g
from . import login_manager, current_user, login_required, auth
from flask_login import login_user, logout_user
from .models import LoginForm, ldap_login

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@auth.before_request
def get_current_user():
    g.user = current_user

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('home'))

    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')

        user = ldap_login(username, password)

        if user is None:
            flash(
                'Invalid username or password. Please try again.',
                'danger')
            return render_template('login.html', form=form)

        login_user(user,remember=remember)
        flash('You have successfully logged in.', 'success')
        return redirect(url_for('home'))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
