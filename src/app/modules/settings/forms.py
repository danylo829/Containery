from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, ColorField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class GlobalSettingsForm(FlaskForm):
    # General Settings
    docker_socket = StringField('Docker socket', validators=[DataRequired()], default="/var/run/docker.sock")
    dashboard_refresh_interval = IntegerField('Dashboard refresh interval', 
                                     validators=[DataRequired(), NumberRange(min=1, max=60)], default=5)
    log_retention_days = IntegerField('Log retention days', 
                                      validators=[DataRequired(), NumberRange(min=1)], default=30)

    # Session and Security Settings
    session_timeout = IntegerField('Session timeout', 
                                   validators=[DataRequired(), NumberRange(min=1)], default=30)
    password_min_length = IntegerField('Password minimum length', 
                                       validators=[DataRequired(), NumberRange(min=6, max=50)], default=8)

    submit = SubmitField('Save')
