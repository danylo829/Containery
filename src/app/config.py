import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    CSRF_SECRET_KEY = os.getenv('CSRF_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:////app_data/containery.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
