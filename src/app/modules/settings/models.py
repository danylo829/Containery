from app.core.extensions import db

class GlobalSettings(db.Model):
    __tablename__ = 'stg_global_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(150), unique=True, nullable=False)
    value = db.Column(db.String(150), nullable=False)

    defaults = {
        'dashboard_refresh_interval': 5,
        'session_timeout': 1800,
        'password_min_length': 8,
        'latest_version': '',
        'latest_version_checked_at': '',
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