from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, SelectField, PasswordField, StringField
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

class ChangeUserRoleForm(FlaskForm):
    role = SelectField(
        'Role', 
        choices=[(role.name, role.value) for role in Role],
        default=Role.READER.value,
        validators=[DataRequired()])
    submit = SubmitField('Change Role', name='change_role')

class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=24, min=1)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField(
        'Role', 
        choices=[(role.name, role.value) for role in Role],
        default=Role.READER.value,
        validators=[DataRequired()])
    submit = SubmitField('Create User', name='create_user')