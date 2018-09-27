"""
instrument_catalog.server
~~~~~~~~~~~~~~~~~~~~~~~~~

Defines server routes, including main application logic.
"""
import os
from flask import Flask, render_template, request, redirect, url_for
from . import db_stub as db


app = Flask(__name__)


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


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


@app.route('/')
def index():
    """Display the home page."""
    return render_template('index.html', instruments=db.get_instruments())


@app.route('/categories/')
def all_categories():
    """Display a list of all instrument categories."""
    return render_template('all_categories.html')


@app.route('/categories/<int:category_id>/')
def one_category(category_id):
    """Display a list of all instruments in a given category."""
    return render_template('one_category.html',
                           category=db.get_category(category_id),
                           instruments=db.get_instruments())


@app.route('/instruments/')
def all_instruments():
    """Display a list of all instruments in all categories."""
    return render_template('all_instruments.html',
                           instruments=db.get_instruments())


@app.route('/instruments/<int:instrument_id>/')
def one_instrument(instrument_id):
    """Display information about a given instrument."""
    return render_template('one_instrument.html',
                           instrument=db.get_instrument(instrument_id))


@app.route('/instruments/new')
def new_instrument():
    """Display a form for creating a new instrument."""
    return render_template('new_instrument.html')


@app.route('/instruments/<int:instrument_id>/edit')
def edit_instrument(instrument_id):
    """Display a form for editing an existing instrument."""
    return render_template('edit_instrument.html',
                           instrument=db.get_instrument(instrument_id))


@app.route('/instruments/<int:instrument_id>/delete')
def delete_instrument(instrument_id):
    """Display a form for deleting an existing instrument."""
    return render_template('delete_instrument.html',
                           instrument=db.get_instrument(instrument_id))


@app.route('/my/')
def my_instruments():
    """Display all instruments that the logged in user has created."""
    return render_template('my_instruments.html',
                           instruments=db.get_instruments())


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Display the login page."""
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        g.user = user
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """Log the user out and redirect to the home page."""
    if hasattr(g, 'user'):
        del g.user
    return redirect(url_for('index'))
