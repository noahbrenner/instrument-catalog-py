"""
instrument_catalog.api
~~~~~~~~~~~~~~~~~~~~~~

Defines routes for JSON API.
"""
from flask import Blueprint, g, jsonify, request
from .models import db, User, Category, Instrument, AlternateInstrumentName


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
        pass


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
