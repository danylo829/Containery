from app.core.extensions import db

class GlobalSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(150), unique=True, nullable=False)
    value = db.Column(db.String(150), nullable=False)

    defaults = {
        'dashboard_refresh_interval': 5,
        'session_timeout': 1800,
        'password_min_length': 8,
    }

    @classmethod
    def get_setting(cls, key):
        if key not in cls.defaults:
            raise KeyError(f"The setting '{key}' is not defined in defaults.")

        try:
            setting = cls.query.filter_by(key=key).first()
            return setting.value if setting else cls.defaults[key]
        except Exception as e:
            raise RuntimeError(f"Database error while retrieving setting '{key}': {str(e)}")

    @classmethod
    def set_setting(cls, key, value):
        if key not in cls.defaults:
            raise KeyError(f"The setting '{key}' is not defined in defaults.")

        if key == 'dashboard_refresh_interval' or key == 'log_retention_days' or key == 'session_timeout':
            try:
                value = int(value)
                if value <= 0:
                    raise ValueError(f"The value for '{key}' must be a positive integer.")
            except ValueError:
                raise ValueError(f"The value for '{key}' must be an integer.")

        try:
            setting = cls.query.filter_by(key=key).first()
            if setting:
                setting.value = str(value)
            else:
                setting = cls(key=key, value=str(value))
                db.session.add(setting)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Database error while setting '{key}': {str(e)}")

    @classmethod
    def delete_setting(cls, key):
        if key not in cls.defaults:
            raise KeyError(f"The setting '{key}' is not defined in defaults.")
        
        try:
            setting = cls.query.filter_by(key=key).first()
            if setting:
                db.session.delete(setting)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Database error while deleting setting '{key}': {str(e)}")