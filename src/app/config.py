class Config:
    SECRET_KEY = '12345678'
    CSRF_SECRET_KEY = '87654321'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////app_data/containery.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True