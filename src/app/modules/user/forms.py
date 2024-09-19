from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length

class PersonalSettingsForm(FlaskForm):
    constrain_tables_view = BooleanField('Constrain tables view')
    theme = SelectField(
        'Theme',
        choices=[('light', 'Light'), ('dark', 'Dark'), ('system', 'System')],
        default='system'
    )
    submit = SubmitField('Save Changes', name='submit_settings')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_new_password = PasswordField('Confirm New Password', 
                                         validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')])
    submit = SubmitField('Change Password', name='submit_password')