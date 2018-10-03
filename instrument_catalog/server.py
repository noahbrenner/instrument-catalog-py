"""
instrument_catalog.server
~~~~~~~~~~~~~~~~~~~~~~~~~

Defines server routes, including main application logic.
"""
import os
import re
from flask import Flask, render_template, request, redirect, url_for
from .models import db, User, Category, Instrument, AlternateInstrumentName


app = Flask(__name__)


# Hacky stub for global object
class g:
    pass


def collapse_spaces(string=None, preserve_newlines=False):
    """Strip outer and extra internal whitespace, preserving newlines."""
    regex = r'[ \t\f\v]+' if preserve_newlines else r'\s+'
    return re.sub(regex, ' ', string.strip()) if string else string


def get_alternate_instrument_names(form):
    """Return a normalized list of alternate names from form input."""
    alt_names = []

    for index in range(10):
        name = form.get('alt_name_{}'.format(index), None)

        if name is None:
            break

        # Eliminate any extra whitespace
        name = collapse_spaces(name)

        if name is not '':
            alt_names.append(name)

    return alt_names


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


@app.route('/instruments/new', methods=['GET', 'POST'])
def new_instrument():
    """Display a form for creating a new instrument."""
    if request.method == 'GET':
        return render_template('new_instrument.html')

    elif request.method == 'POST':
        form = request.form
        instrument = Instrument(name=form['name'],
                                description=form['description'],
                                category_id=form['category_id'],
                                user_id=g.user.id,
                                image=form.get('image', None))

        alt_names = get_alternate_instrument_names(form)

        if alt_names:
            instrument.alternate_names.extend(
                AlternateInstrumentName(name=name, index=index)
                for index, name in enumerate(alt_names))

        db.session.add(instrument)
        db.session.commit()

        return redirect(url_for('one_instrument', instrument_id=instrument.id))


@app.route('/instruments/<int:instrument_id>/edit', methods=['GET', 'POST'])
def edit_instrument(instrument_id):
    """Display a form for editing an existing instrument."""
    instrument = Instrument.query.get(instrument_id)

    if request.method == 'GET':
        return render_template('edit_instrument.html', instrument=instrument)

    elif request.method == 'POST':
        form = request.form

        # Update required columns
        required_columns = ('name', 'description', 'category_id')
        for key in required_columns:
            setattr(instrument, key, form[key])

        # Update optional image column
        instrument.image = request.form.get('image', None)

        # Update alternate names unless they haven't been changed at all
        new_alt_names = get_alternate_instrument_names(form)
        old_alt_names = [alt.name for alt in instrument.alternate_names]

        if not new_alt_names == old_alt_names:
            # Make sure we don't have more rows than new alternate names
            del instrument.alternate_names[len(new_alt_names):]
            # TODO Identify and update existing names to enable atomic commit
            # We need to commit now, before modifying or adding names, to avoid
            # failing a UNIQUE constraint in some situations (e.g. re-ordering
            # rows). This prevents the edit from being atomic, unfortunately.
            db.session.commit()

            # Update or create new alternate names as needed
            for index, name in enumerate(new_alt_names):
                try:
                    instrument.alternate_names[index].name = name
                except IndexError:
                    instrument.alternate_names.append(
                        AlternateInstrumentName(name=name, index=index))

        db.session.commit()

        return redirect(url_for('one_instrument', instrument_id=instrument_id))


@app.route('/instruments/<int:instrument_id>/delete', methods=['GET', 'POST'])
def delete_instrument(instrument_id):
    """Display a form for deleting an existing instrument."""
    instrument = Instrument.query.get(instrument_id)

    if request.method == 'GET':
        return render_template('delete_instrument.html', instrument=instrument)

    elif request.method == 'POST':
        category_id = instrument.category_id
        db.session.delete(instrument)
        db.session.commit()
        return redirect(url_for('one_category', category_id=category_id))


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
            g.user = User.query.get(1)
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """Log the user out and redirect to the home page."""
    if hasattr(g, 'user'):
        del g.user
    return redirect(url_for('index'))
