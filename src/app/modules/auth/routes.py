from flask import render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from app.modules.user.models import Permissions, User, Role
from app.modules.settings.models import GlobalSettings
from .forms import LoginForm, AdminSetupForm

from . import auth

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard.index'))
    if not User.query.first():
        return redirect(url_for('auth.install'))

    form = LoginForm()
    if form.validate_on_submit():
        username = str(form.username.data).strip()
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index.root'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html', form=form)

@auth.route('/install', methods=['GET', 'POST'])
def install():
    if User.query.first():
        return redirect(url_for('index.root'))

    password_min_length = int(GlobalSettings.get_setting('password_min_length'))

    form = AdminSetupForm(min_length=password_min_length)
    
    if form.validate_on_submit():
        username = str(form.username.data).strip()
        password = str(form.password.data)

        if len(password) < password_min_length:
            return redirect(url_for('auth.install'))

        try:
            admin_role = Role.create_role('admin')
            flash(f"Role 'admin' created successfully.", 'success')

            for permission in Permissions:
                try:
                    admin_role.add_permission(permission.value)
                except ValueError as e:
                    flash(str(e), 'error')

            user = User.create_user(username=username, password=password)
            user.assign_role(admin_role)

            flash("Admin user created successfully.", 'success')
            return redirect(url_for('index.root'))

        except ValueError as ve:
            flash(str(ve), 'error')
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}", 'error')

    return render_template('install.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index.root'))