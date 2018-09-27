"""
Instrument Catalog
------------------

A webserver for displaying and editing a catalog of musical instruments.
"""
import os
from flask_migrate import Migrate
from .server import app
from .models import db


__all__ = ['app']

basedir = os.path.abspath(os.path.dirname(__file__))


# Some other settings are applied using environment variables with
# defaults set in the .flaskenv file via the dotenv package
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'),
    SQLALCHEMY_DATABASE_URI=os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'app.db')),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db.init_app(app)
Migrate(app, db)
