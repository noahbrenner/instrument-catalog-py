"""
instrument_catalog.server
~~~~~~~~~~~~~~~~~~~~~~~~~

Defines server routes, including main application logic.
"""
from flask import (Flask, Markup, flash, g, render_template, request, redirect,
                   session, url_for)
import bleach
import mistune
from . import api
from . import auth
from .models import db, User, Category, Instrument, AlternateInstrumentName
from .validation import get_validated_instrument_data


app = Flask(__name__)
app.register_blueprint(api.bp, url_prefix='/api')
app.register_blueprint(auth.bp, url_prefix='')
app.register_blueprint(auth.google_bp, url_prefix='/auth')

markdown = mistune.Markdown(escape=True)  # Users can't enter raw HTML

bleach_args = dict(
    tags=['a', 'blockquote', 'br', 'code', 'em', 'h1', 'h2', 'h3', 'h4', 'h5',
          'h6', 'hr', 'li', 'ol', 'p', 'pre', 'strong', 'ul'],
    attributes={'a': ['href']},
    protocols=['http', 'https'],
    strip=False
)


@app.template_filter('markdown')
def markdown_filter(data, inline=False):
    return Markup(bleach.clean(markdown(data), **bleach_args))


@app.before_request
def get_user():
    if 'user' in session:
        g.user = User.query.get(session['user'])


@app.context_processor
def inject_template_data():
    """Provide category data used by base template for every request."""
    return dict(categories=Category.query.order_by(Category.id).all())


@app.errorhandler(404)
def not_found(error=None):
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

    if category is None:
        return not_found()

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

    if instrument is None:
        return not_found()

    return render_template('one_instrument.html', instrument=instrument)


@app.route('/instruments/new', methods=('GET', 'POST'))
def new_instrument():
    """Display a form for creating a new instrument."""
    if request.method == 'GET':
        return render_template('new_instrument.html')

    elif request.method == 'POST':
        data, valid = get_validated_instrument_data(request.form)

        if not valid:
            return render_template('new_instrument.html', instrument=data)

        instrument = Instrument(name=data['name'],
                                description=data['description'],
                                category_id=data['category_id'],
                                user_id=g.user.id,
                                image=data['image'] or None)

        if 'alternate_names' in data:
            instrument.alternate_names.extend(
                AlternateInstrumentName(name=name, index=index)
                for index, name in enumerate(data['alternate_names']))

        db.session.add(instrument)
        db.session.commit()

        return redirect(url_for('one_instrument', instrument_id=instrument.id))


@app.route('/instruments/<int:instrument_id>/edit', methods=('GET', 'POST'))
def edit_instrument(instrument_id):
    """Display a form for editing an existing instrument."""
    instrument = Instrument.query.get(instrument_id)

    if instrument is None:
        return not_found()

    if request.method == 'GET':
        return render_template('edit_instrument.html',
                               instrument=instrument.serialize())

    elif request.method == 'POST':
        data, valid = get_validated_instrument_data(request.form)

        if not valid:
            # Send cleaned-up (but invalid) data instead of either discarding
            # the user's edits or saving invalid data to the database.
            return render_template('edit_instrument.html', instrument=data)

        # Update columns in instrument table
        for key, value in data.items():
            if not key == 'alternate_names':  # Goes in a different table
                setattr(instrument, key, value)

        # Update alternate names unless they haven't been changed at all
        new_alt_names = data.get('alternate_names', [])
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


@app.route('/instruments/<int:instrument_id>/delete', methods=('GET', 'POST'))
def delete_instrument(instrument_id):
    """Display a form for deleting an existing instrument."""
    instrument = Instrument.query.get(instrument_id)

    if instrument is None:
        return not_found()

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
