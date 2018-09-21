"""
instrument_catalog.server
~~~~~~~~~~~~~~~~~~~~~~~~~

Defines server routes, including main application logic.
"""
import os
from flask import Flask


app = Flask(__name__)
# Other settings are applied using dotenv from .flaskenv file
app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'))


@app.route('/')
def index():
    return 'Home page'
