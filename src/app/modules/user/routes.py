from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

from .forms import *
from app.models import PersonalSettings, User, Role
from app.decorators import role

user = Blueprint('user', __name__, url_prefix='/user', template_folder='templates', static_folder='static')

@user.before_request
@login_required
def before_request():
    pass

@user.route('/profile', methods=['GET', 'POST'])
def profile():
    settings_form = PersonalSettingsForm()
    password_form = ChangeOwnPasswordForm()

    if settings_form.submit.data and settings_form.validate_on_submit():
        PersonalSettings.set_setting(current_user.id, 'constrain_tables_view', 'true' if settings_form.constrain_tables_view.data else 'false')
        PersonalSettings.set_setting(current_user.id, 'theme', settings_form.theme.data)
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('user.profile'))

    if password_form.submit.data and password_form.validate_on_submit():
        if User.check_password(current_user.username, password_form.current_password.data):
            User.update_password(current_user.username, password_form.new_password.data)
            flash('Password updated successfully!', 'success')
        else:
            flash('Current password is incorrect.', 'error')
        return redirect(url_for('user.profile'))
    
    # Set form data based on current settings
    settings_form.constrain_tables_view.data = PersonalSettings.get_setting(current_user.id, 'constrain_tables_view') == 'true'
    settings_form.theme.data = PersonalSettings.get_setting(current_user.id, 'theme')
    
    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": url_for('user.get_list')},
        {"name": current_user.username, "url": None},
    ]
    page_title = 'User info'
    endpoint = "user_info"
    
    return render_template('user/profile.html', 
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title, 
                           settings_form=settings_form, 
                           password_form=password_form)

@user.route('/profile/<int:id>', methods=['GET', 'POST'])
@role([Role.ADMIN], allow=True)
def view_profile(id):
    user = User.query.get_or_404(id)

    password_form = ChangeUserPasswordForm()
    role_form = ChangeUserRoleForm(role=user.role)

    if password_form.submit.data and password_form.validate_on_submit():
        User.update_password(user.username, password_form.new_password.data)
        flash('Pssword changed successfully!', 'success')
        return redirect(url_for('user.view_profile', id=id))

    if role_form.submit.data and role_form.validate_on_submit():
        selected_role = role_form.role.data
        if selected_role not in Role.__members__:
            flash('No such role', 'info')
            return redirect(url_for('user.view_profile', id=id))
        
        result = User.update_role(user.id, Role[selected_role].value)
        if result:
            flash(result, 'error')
            return redirect(url_for('user.view_profile', id=id))

        flash('Role changed successfully!', 'success')
        return redirect(url_for('user.view_profile', id=id))

    role_form.role.value = user.role
    
    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": url_for('user.get_list')},
        {"name": user.username, "url": None},
    ]
    
    page_title = "View Profile"
    
    return render_template('user/view_profile.html', 
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title,
                           password_form=password_form,
                           role_form=role_form,
                           user=user)


@user.route('/add', methods=['GET', 'POST'])
@role([Role.ADMIN], allow=True)
def add():
    add_user_form = AddUserForm()

    if add_user_form.submit.data and add_user_form.validate_on_submit():
        selected_role = add_user_form.role.data
        role = ''
        if selected_role in Role.__members__:
            role = Role[selected_role].value
        else:
            flash('Invalid role selected.', 'error')
            return redirect(url_for('user.add'))

        result = User.create_user(add_user_form.username.data, add_user_form.password.data, role)

        if result:
            flash(result, 'error')
            return redirect(url_for('user.add'))

        flash('User added successfully!', 'success')
        return redirect(url_for('user.get_list'))
    
    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": url_for('user.get_list')},
        {"name": "Add", "url": None},
    ]
    
    page_title = "Add user"
    
    return render_template('user/add.html', 
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title,
                           add_user_form=add_user_form)

@user.route('/delete/<int:user_id>', methods=['POST'])
@role([Role.ADMIN], allow=True)
def delete(user_id):
    result = User.delete_user(user_id)
    
    if result:
        flash('User deleted successfully!', 'success')
    else:
        flash('User deletion failed.', 'error')
    
    return redirect(url_for('user.get_list'))


@user.route('/list', methods=['GET'])
@role([Role.ADMIN], allow=True)
def get_list():
    users = User.query.all()

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": None},
    ]
    page_title = 'User info'
    endpoint = "user_info"
    
    return render_template('user/table.html', 
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title, 
                           users=users)