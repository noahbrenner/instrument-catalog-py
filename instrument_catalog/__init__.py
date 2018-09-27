"""
Instrument Catalog
------------------

A webserver for displaying and editing a catalog of musical instruments.
"""
from .server import app


__all__ = ['app']


# Some other settings are applied using environment variables with
# defaults set in the .flaskenv file via the dotenv package
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key')
)
