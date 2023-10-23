from decouple import config

DATABASE_URI = config("DATABASE_URI")
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgres://", 1)

class Config:
    DEBUG = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = config('SECRET_KEY', default='default-secret-key')
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = 'static'
    STATIC_URL = '/static/'

class ProductionConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    #TEMPLATE_FOLDER = 'templates'

class TestingConfig(Config):
    TESTING = True   