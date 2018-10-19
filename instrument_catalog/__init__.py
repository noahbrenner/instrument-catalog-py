"""
Instrument Catalog
------------------

A webserver for displaying and editing a catalog of musical instruments.
"""
import os
from flask_migrate import Migrate
from werkzeug.contrib.fixers import ProxyFix
from .server import app
from .models import db, Category
from .api import rate_limiter
from .auth import login_manager


__all__ = ['app']

basedir = os.path.abspath(os.path.dirname(__file__))

# For Heroku. See: https://flask-dance.readthedocs.io/en/latest/proxies.html
app.wsgi_app = ProxyFix(app.wsgi_app)

# Some dev-specific settings are applied using environment variables set
# via dotenv from the .flaskenv file. Other settings are here:
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


# Unfortunately, this runs *after* the first request, but before we send a
# response, thus potentially delaying our response to our first visitor.
@app.before_first_request
def initialize_database():
    """Add seed data to the database if it looks like it's empty."""
    with app.app_context():
        if len(Category.query.all()) == 0:
            from . import db_init
            db_init.init()
