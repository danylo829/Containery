from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, SelectField, PasswordField, StringField, FieldList, FormField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Length
from app.models import Role

class PersonalSettingsForm(FlaskForm):
    theme = SelectField(
        'Theme',
        choices=[('light', 'Light'), ('dark', 'Dark'), ('dark_mixed', 'Dark Mixed'), ('system', 'System')],
        default='system'
    )
    submit = SubmitField('Save Changes', name='submit_settings')

class ChangeOwnPasswordForm(FlaskForm):
    def __init__(self, password_min_length=8, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adjust the minimum password length dynamically
        self.new_password.validators.append(
            Length(min=password_min_length, message=f"Password must be at least {password_min_length} characters long.")
        )

    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')]
    )
    submit = SubmitField('Change Password', name='submit_password')

class ChangeUserPasswordForm(FlaskForm):
    def __init__(self, password_min_length=8, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_password.validators.append(
            Length(min=password_min_length, message=f"Password must be at least {password_min_length} characters long.")
        )

    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')]
    )
    submit = SubmitField('Change Password', name='submit_user_password')
    submit = SubmitField('Change Password', name='submit_user_password')

class AddUserRoleForm(FlaskForm):
    role = SelectField(
        'Role', 
        choices=[],
        validators=[DataRequired()]
    )
    submit = SubmitField('Add', name='Add_role')

    def set_role_choices(self, roles):
        if roles:
            self.role.choices = [(role.id, role.name) for role in roles]
        else:
            self.role.choices = [('', 'No available roles')]
            self.submit.render_kw = {'disabled': 'disabled'}

class AddUserForm(FlaskForm):
    def __init__(self, password_min_length=8, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password.validators.append(
            Length(min=password_min_length, message=f"Password must be at least {password_min_length} characters long.")
        )

    username = StringField('Username', validators=[DataRequired(), Length(max=24, min=1)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField(
        'Role',
        choices=[],
        validators=[DataRequired()]
    )
    submit = SubmitField('Create User', name='create_user')

    def set_role_choices(self, roles):
        self.role.choices = [(role.id, role.name) for role in roles]

class PermissionForm(FlaskForm):
    enabled = BooleanField('Enabled')
    permission_value = HiddenField()

class AddRoleForm(FlaskForm):
    role_name = StringField('Role Name')
    permissions = FieldList(FormField(PermissionForm), label='Permissions')
    submit = SubmitField('Add')

class EditRoleForm(FlaskForm):
    role_name = StringField('Role Name')
    permissions = FieldList(FormField(PermissionForm), label='Permissions')
    submit = SubmitField('Save')
