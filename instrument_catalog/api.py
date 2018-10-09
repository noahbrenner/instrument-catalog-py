"""
instrument_catalog.api
~~~~~~~~~~~~~~~~~~~~~~

Defines routes for JSON API.
"""
from flask import Blueprint, g, get_flashed_messages, jsonify, request, url_for
from .models import db, User, Category, Instrument, AlternateInstrumentName
from .validation import get_validated_instrument_data


bp = Blueprint('api', __name__)


# Temporary stub for testing authentication
@bp.before_request
def auth_stub():
    try:
        user_id = int(request.query_string)
    except ValueError:
        pass
    else:
        g.user = User.query.get(user_id)


def api_jsonify(data, errors=None):
    """Return a standardized, JSON-ified response."""
    errors = [] if errors is None else errors
    return jsonify(successful=not errors, errors=errors, data=data)


@bp.route('/categories/')
def categories_api():
    """API endpoint representing all categories."""
    all_categories = [c.serialize() for c in Category.query]
    return api_jsonify(all_categories)


@bp.route('/categories/<int:category_id>/')
def one_category_api(category_id):
    """API endpoint for a single category."""
    one_category = Category.query.get(category_id).serialize()
    return api_jsonify(one_category)


@bp.route('/categories/<int:category_id>/instruments/')
def one_category_instruments_api(category_id):
    """API endpoint for instruments in a single category."""
    category_instruments = [
        instrument.serialize()
        for instrument in Instrument.query.filter_by(category_id=category_id)]

    return api_jsonify(category_instruments)


@bp.route('/instruments/', methods=('GET', 'POST'))
def instruments_api():
    """API endpoint for creating or listing instruments."""
    if request.method == 'GET':
        all_instruments = [i.serialize() for i in Instrument.query]
        return api_jsonify(all_instruments)

    elif request.method == 'POST':
        instrument_data, valid = get_validated_instrument_data(request.json)

        if not valid:
            errors = list(get_flashed_messages())
            return api_jsonify(instrument_data, errors), 400  # Bad Request
        else:
            alternate_names = instrument_data.pop('alternate_names')

            # Create the requested database entry
            instrument = Instrument(user_id=g.user.id, **instrument_data)

            instrument.alternate_names.extend(
                AlternateInstrumentName(name=name, index=index)
                for index, name in enumerate(alternate_names))

            db.session.add(instrument)
            db.session.commit()

            status_code = 201  # Created
            headers = {'Location': url_for('one_instrument',
                                           instrument_id=instrument.id)}
            return api_jsonify(instrument.serialize()), status_code, headers


@bp.route('/instruments/<int:instrument_id>/',
          methods=('GET', 'PUT', 'DELETE'))
def one_instrument_api(instrument_id):
    instrument = Instrument.query.get(instrument_id)

    if request.method == 'GET':
        return api_jsonify(instrument.serialize())

    elif request.method == 'PUT':
        pass

    elif request.method == 'DELETE':
        pass


@bp.route('/myinstruments/')
def my_instruments_api():
    user_instruments = [
        instrument.serialize()
        for instrument in Instrument.query.filter_by(user_id=g.user.id)]

    return api_jsonify(user_instruments)
