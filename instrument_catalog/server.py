"""
instrument_catalog.server
~~~~~~~~~~~~~~~~~~~~~~~~~

Defines server routes, including main application logic.
"""
import os
from flask import Flask, render_template, redirect, url_for
from . import db_stub as db


app = Flask(__name__)
# Other settings are applied using dotenv from .flaskenv file
app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'))


# Hacky stubs for global object and logged-in user
class g:
    pass


class user:
    id = 1


@app.context_processor
def inject_template_data():
    """Provide category data used by base template for every request."""
    return dict(categories=db.get_categories(),
                logged_in=hasattr(g, 'user'),
                g=g)


@app.route('/')
def index():
    """Display the home page."""
    return 'Home page'


@app.route('/categories/')
def all_categories():
    """Display a list of all instrument categories."""
    return 'List all instrument categories.'


@app.route('/categories/<int:category_id>/')
def one_category(category_id):
    """Display a list of all instruments in a given category."""
    return 'List all instruments in category with id {}.'.format(category_id)


@app.route('/instruments/')
def all_instruments():
    """Display a list of all instruments in all categories."""
    return 'List all instruments in all categories.'


@app.route('/instruments/<int:instrument_id>/')
def one_instrument(instrument_id):
    """Display information about a given instrument."""
    return 'Show details of instrument with id {}.'.format(instrument_id)


@app.route('/instruments/new')
def new_instrument():
    """Display a form for creating a new instrument."""
    return 'Create a new instrument.'


@app.route('/instruments/<int:instrument_id>/edit')
def edit_instrument(instrument_id):
    """Display a form for editing an existing instrument."""
    return 'Edit instrument with id {}.'.format(instrument_id)


@app.route('/instruments/<int:instrument_id>/delete')
def delete_instrument(instrument_id):
    """Display a form for deleting an existing instrument."""
    return 'Delete instrument with id {}.'.format(instrument_id)


@app.route('/my/')
def my_instruments():
    """Display all instruments that the logged in user has created."""
    return 'Show all instruments that the logged in user has created.'


@app.route('/login')
def login():
    """Display the login page."""
    g.user = user
    return 'Show the login page.'


@app.route('/logout')
def logout():
    """Log the user out and redirect to the home page."""
    if hasattr(g, 'user'):
        del g.user
    return redirect(url_for('index'))
