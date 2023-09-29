from flask import Blueprint, render_template, redirect, request, flash, url_for
from .models import User, LoginForm, SignupForm
from flask_login import login_user, logout_user, current_user, login_required
from . import lm

auth = Blueprint('auth', __name__)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            return redirect(url_for('auth.signup', **request.args))
        login_user(user, form.remember_me.data)
        return redirect(url_for('views.products'))
    return render_template('login.html', form=form, user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            # add user to db
            User.register(form.username.data, form.password.data)
            return redirect(url_for('views.products'))
        return redirect(url_for('auth.login'))
    return render_template('signup.html', form=form, user=current_user)

