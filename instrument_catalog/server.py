"""
instrument_catalog.server
~~~~~~~~~~~~~~~~~~~~~~~~~

Defines server routes, including main application logic.
"""
import os
from flask import Flask, render_template, request, redirect, url_for
from .models import db, User, Category, Instrument, AlternateInstrumentName


app = Flask(__name__)


# Hacky stub for global object
class g:
    pass


@app.context_processor
def inject_template_data():
    """Provide category data used by base template for every request."""
    return dict(categories=Category.query.order_by(Category.id).all(),
                logged_in=hasattr(g, 'user'),
                g=g)


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


@app.route('/')
def index():
    """Display the home page."""
    # Assume that newer instruments have higher ID values
    new_instruments = Instrument.query.order_by(Instrument.id.desc()).limit(3)
    return render_template('index.html', instruments=new_instruments)


@app.route('/categories/')
def all_categories():
    """Display a list of all instrument categories."""
    # No db query -- category data is injected automatically for all requests
    return render_template('all_categories.html')


@app.route('/categories/<int:category_id>/')
def one_category(category_id):
    """Display a list of all instruments in a given category."""
    category = Category.query.get(category_id)
    return render_template('one_category.html', category=category)


@app.route('/instruments/')
def all_instruments():
    """Display a list of all instruments in all categories."""
    # No db query -- category data is injected automatically for all requests
    # and instrument data is associated with each category.
    # TODO If app scales, we'll want to manually query using `yield_per()`.
    return render_template('all_instruments.html')


@app.route('/instruments/<int:instrument_id>/')
def one_instrument(instrument_id):
    """Display information about a given instrument."""
    instrument = Instrument.query.get(instrument_id)
    return render_template('one_instrument.html', instrument=instrument)


@app.route('/instruments/new')
def new_instrument():
    """Display a form for creating a new instrument."""
    return render_template('new_instrument.html')


@app.route('/instruments/<int:instrument_id>/edit')
def edit_instrument(instrument_id):
    """Display a form for editing an existing instrument."""
    instrument = Instrument.query.get(instrument_id)
    return render_template('edit_instrument.html', instrument=instrument)


@app.route('/instruments/<int:instrument_id>/delete')
def delete_instrument(instrument_id):
    """Display a form for deleting an existing instrument."""
    instrument = Instrument.query.get(instrument_id)
    return render_template('delete_instrument.html', instrument=instrument)


@app.route('/my/')
def my_instruments():
    """Display all instruments that the logged in user has created."""
    instruments = Instrument.query\
        .filter_by(user_id=g.user.id).order_by(Instrument.name).all()
    return render_template('my_instruments.html', instruments=instruments)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Display the login page."""
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        if app.config['ENV'] == 'development':
            g.user = User.query.get(0)
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """Log the user out and redirect to the home page."""
    if hasattr(g, 'user'):
        del g.user
    return redirect(url_for('index'))
