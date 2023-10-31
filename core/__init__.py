from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from decouple import config
from core.models import db
from core.auth import login_manager
from core.app import app

#app = Flask(__name__)

# load configuration variables from a configuration file
# load configuration settings
app.config.from_object(config("APP_SETTINGS"))

# initialize a database connection
# db = SQLAlchemy(app)

migrate = Migrate(app, db, render_as_batch=True)
db.init_app(app)

login_manager.init_app(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'

bootstrap = Bootstrap(app)

# import other modules in the package
from core import routes