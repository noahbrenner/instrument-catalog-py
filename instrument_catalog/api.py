"""
instrument_catalog.api
~~~~~~~~~~~~~~~~~~~~~~

Defines routes for JSON API.
"""
from flask import (Blueprint, Markup, get_flashed_messages, jsonify, redirect,
                   render_template, request, url_for)
from flask_limiter import Limiter
from flask_login import current_user, login_required
import mistune
import pygments
from .models import db, User, Category, Instrument, AlternateInstrumentName
from .validation import get_validated_instrument_data


bp = Blueprint('api', __name__)

documentation_bp = Blueprint('documentation', __name__,
                             template_folder='doc')

# TODO If app scales, we'll want to use `moving-window` and redis
rate_limiter = Limiter(strategy='fixed-window',
                       storage_uri='memory://',
                       key_func=lambda: current_user.id)

rate_limit = rate_limiter.shared_limit('50/minute;2/second', scope='api')


def api_jsonify(data, errors=None):
    """Return a standardized, JSON-ified response."""
    errors = [] if errors is None else errors
    return jsonify(successful=not errors, errors=errors, data=data)


# Event handlers

@bp.before_request
def require_authentication():
    """Return an error for any unauthenticated API request."""
    # Instead of adding a `@login_required` decorator to every API route, we're
    # directly verifying every request that is processed by this blueprint.
    # Because of the wildcard `api_not_found` route, any request starting with
    # the URL prefix (or subdomain) associated with this blueprint will cause
    # this `before_request` handler to be called. Benefits of this approach:
    #
    #  - All possible endpoints are handled at once, including non-existent
    #    or misspelled ones.
    #  - A session cookie is not sent for any intended API request.
    if not current_user.is_authenticated:
        errors = ['You must authenticate using the `Authorization: Bearer`'
                  ' header in order to make API calls. Find your API key by'
                  ' visiting this URL in your browser: {url}'
                  .format(url=url_for('documentation.api', _external=True))]

        return api_jsonify({}, errors), 403  # Forbidden


@bp.errorhandler(429)
def rate_limit_handler(error):
    """Return JSON response for requests over the rate limit."""
    errors = ['Rate limit exceeded: {}'.format(error.description)]
    return api_jsonify({}, errors), 429


# Custom markdown rendering

class CodeHighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        if lang:
            lexer = pygments.lexers.get_lexer_by_name(lang, stripall=True)
            formatter = pygments.formatters.html.HtmlFormatter()
            return pygments.highlight(code, lexer, formatter)
        else:
            return '\n<pre><code>{code_block}</code></pre>\n'.format(
                code_block=mistune.escape(code))


markdown = mistune.Markdown(renderer=CodeHighlightRenderer())


@documentation_bp.app_template_filter('doc_markdown')
def doc_markdown_filter(data, inline=False):
    print('Received call to render markdown.')
    return Markup(markdown(data))


# Routes

@documentation_bp.route('/')
def api_doc():
    """Display API documentation webpage."""
    return render_template('api.html')


@bp.route('/categories/')
@rate_limit
def categories_api():
    """API endpoint representing all categories."""
    all_categories = [c.serialize() for c in Category.query]
    return api_jsonify(all_categories)


@bp.route('/categories/<int:category_id>/')
@rate_limit
def one_category_api(category_id):
    """API endpoint for a single category."""
    one_category = Category.query.get(category_id).serialize()
    return api_jsonify(one_category)


@bp.route('/categories/<int:category_id>/instruments/')
@rate_limit
def one_category_instruments_api(category_id):
    """API endpoint for instruments in a single category."""
    category_instruments = [
        instrument.serialize()
        for instrument in Instrument.query.filter_by(category_id=category_id)]

    return api_jsonify(category_instruments)


@bp.route('/instruments/', methods=['GET', 'POST'])
@rate_limit
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
            instrument = Instrument(user_id=current_user.id, **instrument_data)

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
          methods=['GET', 'PUT', 'DELETE'])
@rate_limit
def one_instrument_api(instrument_id):
    instrument = Instrument.query.get(instrument_id)

    # We can't return or modify a non-existent instrument, but DELETE is OK
    if instrument is None and request.method != 'DELETE':
        errors = ['The requested instrument id does not exist.']
        return api_jsonify({}, errors), 404  # Not Found

    if request.method == 'GET':
        return api_jsonify(instrument.serialize())

    elif request.method == 'PUT':
        # Only the user who created `instrument` can modify it
        if instrument.user_id != current_user.id:
            errors = ['You must authenticate as the user who created'
                      ' this instrument in order to modify it.']
            return api_jsonify({}, errors), 403  # Forbidden

        instrument_data, valid = get_validated_instrument_data(
            request.json, existing_instrument=instrument.serialize())

        if not valid:
            errors = list(get_flashed_messages())
            instrument_data['id'] = instrument_id  # Help with debugging
            return api_jsonify(instrument_data, errors), 400  # Bad Request
        else:
            new_alt_names = instrument_data.pop('alternate_names')
            old_alt_names = [alt.name for alt in instrument.alternate_names]

            for key, value in instrument_data.keys():
                setattr(instrument, key, value)

            if new_alternate_names != old_alt_names:
                # Make sure we don't have more rows than new alternate names
                del instrument.alternate_names[len(new_alt_names):]
                # TODO Figure out how to make an atomic commit
                # We need to commit now, before modifying or adding names, to
                # avoid failing a UNIQUE constraint in some situations.
                # Committing early prevents the edit from being atomic.
                db.session.commit()

                # Update or create new alternate names as needed
                for index, name in enumerate(new_alt_names):
                    try:
                        instrument.alternate_names[index].name = name
                    except IndexError:
                        instrument.alternate_names.append(
                            AlternateInstrumentName(name=name, index=index))

            db.session.commit()  # TODO put this in a try...except block?
            return api_jsonify(instrument.serialize()), 200  # OK

    elif request.method == 'DELETE':
        # DELETE requests are idempotent, so we return a successful response
        # even if `instrument_id` is not in the database.
        if instrument is not None:
            if instrument.user_id == current_user.id:
                db.session.delete(instrument)
                db.session.commit()
            else:
                errors = ['You must authenticate as the user who created'
                          ' this instrument in order to modify it.']
                data = {'instrument_id': instrument_id}
                return api_jsonify(data, errors), 403  # Forbidden

        data = {'deleted_instrument_id': instrument_id}
        return api_jsonify(data), 200  # OK


@bp.route('/myinstruments/')
@rate_limit
def my_instruments_api():
    """API endpoint for instruments that the authenticated user created."""
    user_instruments = [
        instrument.serialize()
        for instrument in Instrument.query.filter_by(user_id=current_user.id)]

    return api_jsonify(user_instruments)


# NOTE This route must be the last one defined so it doesn't override others
@bp.route('/', defaults={'unused': ''})
@bp.route('/<path:unused>')
def api_not_found(unused):
    """Handle requests to otherwise undefined API endpoint paths."""
    if unused == '':
        return redirect(url_for('documentation.api_doc'))

    return api_jsonify({}, ['Unknown API endpoint.']), 404
