from os import getenv

class Config:
    SECRET_KEY = getenv('SECRET_KEY')
    CSRF_SECRET_KEY = getenv('CSRF_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:////app_data/containery.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'
    DEBUG = getenv('DEBUG', 'False') == 'True'
    STAGE= getenv('STAGE')
