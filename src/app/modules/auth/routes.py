from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Role, GlobalSettings
from .forms import LoginForm, AdminSetupForm

auth = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates', static_folder='static')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard.index'))
    if not User.query.first():
        return redirect(url_for('auth.install'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if User.check_password(username, password):
            user = User.query.filter_by(username=username).first()
            login_user(user)
            return redirect(url_for('index.root'))
        else:
            error = "Invalid username or password"
            flash(error, 'danger')
    return render_template('login.html', form=form)

@auth.route('/install', methods=['GET', 'POST'])
def install():
    if User.query.first():
        return redirect(url_for('index.root'))

    form = AdminSetupForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        result = User.create_user(username=username, password=password, role=Role.ADMIN.value)
        if result:
            flash(result[1], result[0])
        else:
            for key, config in GlobalSettings.defaults.items():
                GlobalSettings.set_setting(key, config['default'])

            return redirect(url_for('index.root'))

    return render_template('install.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index.root'))