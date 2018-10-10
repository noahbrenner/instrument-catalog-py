"""
instrument_catalog.validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Validates user input from instrument create/edit form.
"""
import re
from flask import flash, request
import requests
from requests import Timeout, ConnectionError
from .models import Category, Instrument, AlternateInstrumentName


def collapse_spaces(string=None, markdown_compatible=False):
    """Strip outer and extra internal whitespace, preserving newlines."""
    if markdown_compatible:
        # Don't remove inner whitespace in case the user intended a <br>
        # by writing trailing spaces on a line other than the last one.
        return string.strip() if string else string
    else:
        return re.sub(r'\s+', ' ', string.strip()) if string else string


def get_alternate_instrument_names(form):
    """Return a normalized list of alternate names from form input."""
    # From the API, we receive a list of alternate names directly
    if 'alternate_names' in form:
        if isinstance(form.get('alternate_names'), list):
            alt_names = [collapse_spaces(str(name))
                         for name in form['alternate_names']
                         if name]
        else:
            flash('`alternate_names` must be an array of strings.')
            alt_names = []

    # From the HTML form, each alternate name is a separate field
    else:
        alt_names = []

        for index in range(10):
            name_key = 'alt_name_{}'.format(index)

            if name_key not in form:
                break

            name = collapse_spaces(str(form.get(name_key, '')))

            if name is not '':
                alt_names.append(name)

    return alt_names


def validate_image_url(url):
    """Return validity of an image URL and the result of any redirection."""
    is_valid = True

    # Test: URL uses http(s)
    if not url.startswith('http'):
        is_valid = False
        flash('Image URL: URL must start with "http" or "https"')
    else:
        headers = {'user-agent': 'instrument-catalog'}
        try:
            response = requests.head(url, headers=headers, timeout=2.0,
                                     allow_redirects=True)
        # Test: Image host server responds
        except (Timeout, ConnectionError):
            is_valid = False
            flash('Image URL: The image server could not be reached.'
                  ' Double check the URL or try a different one.')
        else:
            # Test: Image server returns successful response
            if response.status_code is not 200:
                is_valid = False
                flash('Image URL: A request for the image failed'
                      ' with status code {}.'.format(response.status_code))

            # Test: Image has a supported filetype
            elif response.headers.get('Content-Type').lower() not in (
                    'image/jpeg', 'image/png', 'image/gif'):
                is_valid = False
                flash('Image URL: The image must be a jpg, png, or gif.')

            else:
                # Test: Content-Length exists and is smaller than 300 KB
                content_length = int(response.headers.get('Content-Length', 0))

                if not 0 < content_length < 1024 * 300:
                    is_valid = False
                    flash('Image URL: The image must be under 300 KB.')

                # Update the URL in case there was a redirect (we waited to
                # confirm that the URL was valid before doing this)
                url = response.url

    return url, is_valid


def get_validated_instrument_data(form, existing_instrument=None):
    """Validate and return normalized data from instrument form or API.

    Args:
        existing_instrument (Instrument): An optional argument, only
            needed when the key 'name' is not included in `form`.

    Returns:
        tuple[dict, bool]: The normalized data and whether it is valid.
                           The dict's structure is analogous to the
                           output of Instrument.serialize().
    """
    is_valid = True

    # === Copy form data into `instrument` and normalize values === #

    instrument = {}

    # `id` and `user_id` are not validated; their validity is context-dependent
    instrument_table_columns = ['name', 'description', 'image', 'category_id']

    for key in instrument_table_columns:
        if key in form:
            instrument[key] = collapse_spaces(
                str(form.get(key, '')),
                markdown_compatible=(key == 'description'))

    alternate_names = get_alternate_instrument_names(form)
    if alternate_names:
        instrument['alternate_names'] = alternate_names

    # Reference variables
    required_columns = {'name', 'category_id', 'description'}
    string_columns = {'name', 'description', 'image'}
    input_columns = set(key for key, value in instrument.items()
                        if value or value is not 0)

    # === Begin tests === #

    # Test: All required fields are present and are not blank
    if not required_columns.issubset(input_columns):
        # PUT requests do not need to specify all fields, only those to update
        if request.method != 'PUT':
            is_valid = False
            flash('Required data is missing: {columns}'
                  .format(columns=', '.join(required_columns - input_columns)))

    if any(key in string_columns for key in input_columns):
        db_instrument_columns = Instrument.__table__.c

        # Test: No string for the instrument table is over its character limit
        for column in input_columns.intersection(string_columns):
            length_limit = db_instrument_columns[column].type.length

            if len(instrument[column]) > length_limit:
                is_valid = False
                flash('Provided {field} is over the limit of {num} characters.'
                      .format(field=column, num=limit))

    if 'alternate_names' in instrument:
        # Test: No alternate name is over the character limit
        length_limit = AlternateInstrumentName.__table__.c['name'].type.length

        for name in instrument['alternate_names']:
            if len(name) > length_limit:
                is_valid = False
                flash('Alternate name "{name}" is over the limit of'
                      ' {num} characters.'.format(name=name, num=length_limit))

        # Test: Alternate names do not duplicate primary name
        instrument_name = instrument.get('name', existing_instrument.id)

        if instrument_name in instrument['alternate_names']:
            is_valid = False
            flash('Alternate names must not include the primary name.')

        # Test: Alternate names do not duplicate each other
        if len(alternate_names) > len(set(alternate_names)):
            is_valid = False
            flash('Alternate names must not duplicate other alternate names.')

    if 'category_id' in instrument:
        # If the 'category_id' is '', it has already been reported as missing
        if not instrument['category_id'] == '':
            try:
                # Test: Category ID is an integer (NOTE '1.2' becomes 1)
                instrument['category_id'] = int(instrument['category_id'])
            except ValueError:
                is_valid = False
                flash('An invalid category ID was provided.')
            else:
                # Test: Category exists in the database
                if Category.query.get(instrument['category_id']) is None:
                    is_valid = False
                    flash('An invalid category ID was provided.')

    if 'image' in instrument:
        # Test: Image URL is valid and meets our requirements
        validated_url, image_is_valid = validate_image_url(instrument['image'])

        instrument['image'] = validated_url
        is_valid = is_valid and image_is_valid

    return instrument, is_valid