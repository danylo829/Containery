from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from .forms import PersonalSettingsForm, ChangePasswordForm
from app.models import PersonalSettings, User

user = Blueprint('user', __name__, url_prefix='/user', template_folder='templates', static_folder='static')

@user.before_request
@login_required
def before_request():
    pass

@user.route('/profile', methods=['GET', 'POST'])
@login_required
def info():
    settings_form = PersonalSettingsForm()
    password_form = ChangePasswordForm()

    if settings_form.submit.data and settings_form.validate_on_submit():
        PersonalSettings.set_setting(current_user.id, 'constrain_tables_view', 'true' if settings_form.constrain_tables_view.data else 'false')
        PersonalSettings.set_setting(current_user.id, 'theme', settings_form.theme.data)
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('user.info'))

    if password_form.submit.data and password_form.validate_on_submit():
        if User.check_password(current_user.username, password_form.current_password.data):
            User.update_password(current_user.username, password_form.new_password.data)
            flash('Password updated successfully!', 'success')
        else:
            flash('Current password is incorrect.', 'error')
        return redirect(url_for('user.info'))
    
    # Set form data based on current settings
    settings_form.constrain_tables_view.data = PersonalSettings.get_setting(current_user.id, 'constrain_tables_view') == 'true'
    settings_form.theme.data = PersonalSettings.get_setting(current_user.id, 'theme')
    
    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "User", "url": url_for('user.info')},
        {"name": current_user.username, "url": None},
    ]
    page_title = 'User info'
    endpoint = "user_info"
    
    return render_template('user/info.html', 
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title, 
                           settings_form=settings_form, 
                           password_form=password_form)
