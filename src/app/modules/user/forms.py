from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, SelectField, PasswordField, StringField, FieldList, FormField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Length
from app.models import Role

class PersonalSettingsForm(FlaskForm):
    constrain_tables_view = BooleanField('Constrain tables view')
    theme = SelectField(
        'Theme',
        choices=[('light', 'Light'), ('dark', 'Dark'), ('dark_mixed', 'Dark Mixed'), ('system', 'System')],
        default='system'
    )
    submit = SubmitField('Save Changes', name='submit_settings')

class ChangeOwnPasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_new_password = PasswordField('Confirm New Password', 
                                         validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')])
    submit = SubmitField('Change Password', name='submit_password')

class ChangeUserPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_new_password = PasswordField('Confirm New Password', 
                                         validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')])
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
    username = StringField('Username', validators=[DataRequired(), Length(max=24, min=1)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField(
        'Role', 
        choices=[],
        validators=[DataRequired()])
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
