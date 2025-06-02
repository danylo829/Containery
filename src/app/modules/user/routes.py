from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user

from .forms import *
from .models import PersonalSettings, User, Role, Permissions

from app.modules.settings.models import GlobalSettings
from app.core.decorators import permission

from . import user

@user.route('/profile', methods=['GET', 'POST'])
def profile():
    password_min_length = int(GlobalSettings.get_setting('password_min_length'))

    settings_form = PersonalSettingsForm()
    password_form = ChangeOwnPasswordForm(password_min_length=password_min_length)

    if settings_form.submit.data and settings_form.validate_on_submit():
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
    settings_form.theme.data = PersonalSettings.get_setting(current_user.id, 'theme')

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": url_for('user.get_list')},
        {"name": current_user.username, "url": None},
    ]
    page_title = 'Profile'
    
    return render_template('user/profile.html', 
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title, 
                           settings_form=settings_form, 
                           password_form=password_form)

@user.route('', methods=['GET', 'POST'])
@permission(Permissions.USER_VIEW_PROFILE)
def view_profile():
    user_id = request.args.get('id', type=int)
    user = User.query.get(user_id)
    
    if not user_id or not user:
        message = 'No such user.'
        code = 404
        return render_template('error.html', message=message, code=code), code

    password_min_length = int(GlobalSettings.get_setting('password_min_length'))

    password_form = ChangeUserPasswordForm(password_min_length=password_min_length)
    role_form = AddUserRoleForm()

    all_roles = Role.get_roles()
    user_roles = user.get_roles()
    available_roles = [role for role in all_roles if role not in user_roles]
    role_form.set_role_choices(available_roles)

    if request.method == 'POST' and not current_user.has_permission(Permissions.USER_EDIT):
        flash('You cannot edit users', 'error')
        return redirect(url_for('user.view_profile', id=user_id))

    if password_form.submit.data and password_form.validate_on_submit():
        if len(str(password_form.new_password.data)) < password_min_length:
            flash(f'Password length must be at least {password_min_length} characters long.', 'error')
            return redirect(url_for('user.view_profile', id=user_id))
            
        user.update_password(password_form.new_password.data)
        flash('Password changed successfully!', 'success')
        return redirect(url_for('user.view_profile', id=user_id))

    if role_form.submit.data and role_form.validate_on_submit():
        role = Role.get_role(int(role_form.role.data))
        try:
            user.assign_role(role)
            flash(f"Role '{role.name}' assigned successfully.", 'success')
        except (ValueError, LookupError) as e:
            flash(str(e), 'error')

        return redirect(url_for('user.view_profile', id=user_id))

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

@user.route('/remove_role', methods=['DELETE'])
@permission(Permissions.ROLE_EDIT)
def remove_role():
    user_id = request.form.get('user_id')
    role_id = request.form.get('role_id')

    try:
        user = User.query.get(user_id)
        role = Role.get_role(int(role_id))

        user.remove_role(role)

        return jsonify({'success': True}), 200
    
    except PermissionError as pe:
        return jsonify({'message': str(pe)}), 403

    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400

    except LookupError as le:
        return jsonify({'message': str(le)}), 404

    except RuntimeError as re:
        return jsonify({'message': 'Failed to remove role.'}), 500



@user.route('/add', methods=['GET', 'POST'])
@permission(Permissions.USER_ADD)
def add():
    password_min_length = int(GlobalSettings.get_setting('password_min_length'))

    add_user_form = AddUserForm(password_min_length=password_min_length)
    add_user_form.set_role_choices(Role.get_roles())

    if add_user_form.submit.data and add_user_form.validate_on_submit():
        role_id = int(add_user_form.role.data)

        if len(str(add_user_form.password.data)) < password_min_length:
            flash(f'Minimal password length is {password_min_length} characters', 'error')
            return redirect(url_for('user.add'))

        user = User.create_user(add_user_form.username.data, add_user_form.password.data)

        if not isinstance(user, User):
            flash(user, 'error')
            return redirect(url_for('user.add'))

        result = user.assign_role(Role.get_role(role_id))
        if result:
            flash(result)

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

@user.route('/delete', methods=['DELETE'])
@permission(Permissions.USER_DELETE)
def delete():
    user_id = request.args.get('id', type=int)

    try:
        User.delete_user(int(user_id))
        return jsonify({'message': 'User deleted successfully.'}), 200

    except PermissionError as pe:
        return jsonify({'message': str(pe)}), 403

    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400

    except LookupError as le:
        return jsonify({'message': str(le)}), 404

    except RuntimeError as re:
        return jsonify({'message': 'Failed to delete user.'}), 500


@user.route('/list', methods=['GET'])
@permission(Permissions.USER_VIEW_LIST)
def get_list():
    users = User.query.all()

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": None},
    ]
    page_title = 'Users info'
    endpoint = "user_info"
    
    return render_template('user/table.html', 
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title, 
                           users=users)

@user.route('/role/list', methods=['GET'])
@permission(Permissions.ROLE_VIEW_LIST)
def get_role_list():
    roles = Role.get_roles()
    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": url_for('user.get_list')},
        {"name": "Roles", "url": None},
    ]
    page_title = 'Roles'
    
    return render_template('user/table_role.html', 
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title, 
                           roles=roles)

@user.route('/role', methods=['GET', 'POST'])
@permission(Permissions.ROLE_VIEW)
def view_role():
    form = RoleForm()

    role_id = request.args.get('id', type=int)

    try:
        role = Role.get_role(id=role_id)
    except ValueError as ve:
        flash(str(ve), 'error')
        return redirect(url_for('user.get_role_list'))
    except LookupError as le:
        flash(str(le), 'error')
        return redirect(url_for('user.get_role_list'))

    if form.validate_on_submit():
        if role_id == 1:
            flash('Can\'t edit super admin role.', 'error')
            return redirect(url_for('user.get_role_list'))
        if not current_user.has_permission(Permissions.ROLE_EDIT):
            flash('You don\'t have permission to edit roles', 'error')
            return redirect(url_for('user.view_role', id=role_id))

        name = str(form.name.data).strip()
        selected_permissions = [
            int(entry['permission_value'])
            for entry in form.permissions.data if entry['enabled']
        ]

        try:
            role.rename(name)

            for permission in selected_permissions:
                if permission not in role.get_permissions():
                    role.add_permission(permission=permission)

            for permission in role.get_permissions():
                if permission not in selected_permissions:
                    role.remove_permission(permission=permission)

            flash(f"Role '{name}' updated successfully", 'success')

        except ValueError as ve:
            flash(str(ve), 'error')
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}", 'error')
        
        return redirect(url_for('user.view_role', id=role_id))
    
    if not form.permissions.entries:
        for permission in Permissions:
            is_enabled = permission.value in role.get_permissions_values()
            form.permissions.append_entry({
                'enabled': is_enabled,
                'permission_value': permission.value
            })

    form.name.data = role.name

    category_order = ['CONTAINER', 'IMAGE', 'NETWORK', 'VOLUME', 'USER', 'ROLE', 'GLOBAL']

    categories = {}
    for permission_form, permission in zip(form.permissions, Permissions):
        category = permission.name.split('_')[0]
        if category not in categories:
            categories[category] = []
        categories[category].append((permission_form, permission))

    ordered_categories = {cat: categories[cat] for cat in category_order if cat in categories}

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": url_for('user.get_list')},
        {"name": "Roles", "url": url_for('user.get_role_list')},
        {"name": role.name, "url": None},
    ]
    
    page_title = "View Role"
    
    return render_template('user/role.html',
                           breadcrumbs=breadcrumbs,
                           page_title=page_title,
                           role=role,
                           form=form,
                           categories=ordered_categories)

@user.route('/role/add', methods=['GET', 'POST'])
@permission(Permissions.ROLE_ADD)
def add_role():
    form = RoleForm()

    if not form.permissions.entries:
        for permission in Permissions:
            form.permissions.append_entry({
                'enabled': False,
                'permission_value': permission.value
            })

    if form.validate_on_submit():
        name = str(form.name.data).strip()
        selected_permissions = [
            int(entry['permission_value'])
            for entry in form.permissions.data if entry['enabled']
        ]

        try:
            role = Role.create_role(name)
            flash(f"Role '{name}' created successfully", 'success')

            for permission in selected_permissions:
                role.add_permission(permission=permission)

            return redirect(url_for('user.get_role_list'))

        except ValueError as ve:
            flash(str(ve), 'error')
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}", 'error')
    elif request.method == 'POST':
        flash('Form validation failed.', 'error')

    category_order = ['CONTAINER', 'IMAGE', 'NETWORK', 'VOLUME', 'USER', 'ROLE', 'GLOBAL']

    categories = {}
    for permission_form, permission in zip(form.permissions, Permissions):
        category = permission.name.split('_')[0]
        if category not in categories:
            categories[category] = []
        categories[category].append((permission_form, permission))

    ordered_categories = {cat: categories[cat] for cat in category_order if cat in categories}

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Users", "url": url_for('user.get_list')},
        {"name": "Roles", "url": url_for('user.get_role_list')},
        {"name": "Add", "url": None},
    ]
    
    page_title = "Add role"

    return render_template('user/role.html',
                           breadcrumbs=breadcrumbs,
                           page_title=page_title,
                           form=form,
                           categories=ordered_categories)

@user.route('/role/delete', methods=['DELETE'])
@permission(Permissions.ROLE_EDIT)
def delete_role():
    role_id = request.args.get('id', type=int)

    if not role_id:
        return jsonify({'message': 'Role ID is required.'}), 400

    try:
        Role.delete_role(role_id)

        return jsonify({'success': True}), 200

    except PermissionError as pe:
        return jsonify({'message': str(pe)}), 403

    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400

    except LookupError as le:
        return jsonify({'message': str(le)}), 404

    except RuntimeError as re:
        return jsonify({'message': 'Failed to delete role.'}), 500

