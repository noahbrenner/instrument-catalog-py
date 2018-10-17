"""
Instrument Catalog
------------------

A webserver for displaying and editing a catalog of musical instruments.
"""
import os
from flask_migrate import Migrate
from .server import app
from .models import db, Category
from .api import rate_limiter
from .auth import login_manager


__all__ = ['app']

basedir = os.path.abspath(os.path.dirname(__file__))


# Some other settings are applied using environment variables with
# defaults set in the .flaskenv file via the dotenv package
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'),
    SQLALCHEMY_DATABASE_URI=os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'app.db')),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    GOOGLE_OAUTH_CLIENT_ID=os.environ.get('GOOGLE_CLIENT_ID'),
    GOOGLE_OAUTH_CLIENT_SECRET=os.environ.get('GOOGLE_CLIENT_SECRET')
)

db.init_app(app)
Migrate(app, db)
rate_limiter.init_app(app)
login_manager.init_app(app)


# Initialize rows in the database if they don't exist yet
# NOTE This is a side effect: The database may change just from importing
with app.app_context():
    if len(Category.query.all()) == 0:
        from . import db_init
        db_init.init()
