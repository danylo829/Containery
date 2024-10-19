from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Role, Permissions, GlobalSettings
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

    form = AdminSetupForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        try:
            admin_role = Role.create_role('admin')
            flash(f"Role 'admin' created successfully.", 'success')

            for permission in Permissions:
                try:
                    admin_role.add_permission(permission)
                except ValueError as e:
                    flash(str(e), 'error')

            user = User.create_user(username=username, password=password)
            user.assign_role(admin_role)

            for key, config in GlobalSettings.defaults.items():
                GlobalSettings.set_setting(key, config['default'])

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