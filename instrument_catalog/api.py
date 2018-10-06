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


def api_jsonify(errors, data):
    return jsonify(successful=not errors, errors=errors, data=data)


@bp.route('/categories/')
def categories_api():
    """API endpoint representing all categories."""
    errors = []
    categories_data = [c.serialize() for c in Category.query]
    return api_jsonify(errors, categories_data)


@bp.route('/categories/<int:category_id>/')
def one_category_api(category_id):
    """API endpoint for a single category."""
    errors = []
    category_data = Category.query.get(category_id).serialize()
    return api_jsonify(errors, category_data)


@bp.route('/categories/<int:category_id>/instruments/')
def one_category_instruments_api(category_id):
    """API endpoint for instruments in a single category."""
    errors = []
    instruments_data = [i.serialize() for i in Instrument.query.filter_by(
                        category_id=category_id)]
    return api_jsonify(errors, instruments_data)


@bp.route('/instruments/', methods=('GET', 'POST'))
def instruments_api():
    """API endpoint for creating or listing instruments."""
    errors = []

    if request.method == 'GET':
        instruments_data = [i.serialize() for i in Instrument.query]
        return api_jsonify(errors, instruments_data)

    elif request.method == 'POST':
        pass


@bp.route('/instruments/<int:instrument_id>/',
          methods=('GET', 'PUT', 'DELETE'))
def one_instrument_api(instrument_id):
    errors = []
    instrument = Instrument.query.get(instrument_id)

    if request.method == 'GET':
        return api_jsonify(errors, instrument.serialize())

    elif request.method == 'PUT':
        pass

    elif request.method == 'DELETE':
        pass


@bp.route('/myinstruments/')
def my_instruments_api():
    errors = []
    instruments_data = [i.serialize() for i in Instrument.query.filter_by(
                        user_id=g.user.id)]

    return api_jsonify(errors, instruments_data)
