from decouple import config

class Config:
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = config('SECRET_KEY', 'default-secret-key')

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