from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from decouple import config

app = Flask(__name__)

# load configuration variables from a configuration file
# load configuration settings
app.config.from_object(config("APP_SETTINGS"))

# initialize a database connection
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# import other modules in the package
from core import routes