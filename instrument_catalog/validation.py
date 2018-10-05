"""
instrument_catalog.validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Validates user input from instrument create/edit form.
"""
import re
from flask import flash
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
    alt_names = []

    for index in range(10):
        name = form.get('alt_name_{}'.format(index), None)

        if name is None:
            break

        name = collapse_spaces(name)

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


def get_validated_instrument_data(form, instrument_id=None):
    """Validate and return normalized data from instrument form.

    Returns:
        tuple[dict, bool]: The normalized data and whether it is valid.
                           The dict's structure is analogous to the
                           output of Instrument.serialize().
    """
    is_valid = True

    # Copy form data into `instrument`, while normalizing values
    instrument = {
            'name': collapse_spaces(form.get('name', '')),
            'description': collapse_spaces(form.get('description', ''),
                                           markdown_compatible=True),
            'image': collapse_spaces(form.get('image')) or None,
            'category_id': collapse_spaces(form.get('category_id', '')),
            'alternate_names': get_alternate_instrument_names(form)
    }
    # `instrument_id` exists when editing, not when creating a new instrument
    if instrument_id:
        instrument['id'] = instrument_id

    required_columns = {'name', 'category_id', 'description'}
    string_columns = ['name', 'description', 'image']
    input_columns = set(instrument.keys())
    input_alternate_names = instrument['alternate_names']

    # Test: All required fields are present and are not blank
    if not (required_columns.issubset(input_columns)
            and all(instrument[key] for key in required_columns)):
        is_valid = False
        flash('Required data is missing: {columns}'
              .format(columns=', '.join(required_columns - input_columns)))

    # Test: No string for the instrument table is over its character limit
    db_instrument_columns = Instrument.__table__.c
    oversized_instrument_columns = []

    for column in string_columns:
        limit = db_instrument_columns[column].type.length
        if instrument[column] and len(instrument[column]) > limit:
            oversized_instrument_columns.append((column, limit))

    if oversized_instrument_columns:
        is_valid = False
        for column, limit in oversized_instrument_columns:
            flash('Instrument {field} is over the limit of {num} characters.'
                  .format(field=column, num=limit))

    # Test: No alternate name is over the character limit
    alt_name_limit = AlternateInstrumentName.__table__.c['name'].type.length
    oversized_alt_names = [name for name in input_alternate_names
                           if len(name) > alt_name_limit]
    if oversized_alt_names:
        is_valid = False
        for name in oversized_alt_names:
            flash('Alternate name "{name}" is over the limit of'
                  ' {num} characters.'.format(name=name, num=alt_name_limit))

    # Test: Alternate names do not duplicate primary name
    if instrument.get('name') in input_alternate_names:
        is_valid = False
        flash('Alternate names must not include the primary name.')

    # Test: Alternate names do not duplicate each other
    if len(input_alternate_names) > len(set(input_alternate_names)):
        is_valid = False
        flash('Alternate names must not duplicate other alternate names.')

    try:
        # Test: Category ID is an integer
        instrument['category_id'] = int(instrument['category_id'])
    except ValueError:
        is_valid = False
        flash('An invalid category ID was provided.')
    else:
        # Test: Category exists in the database
        if Category.query.get(instrument.get('category_id')) is None:
            is_valid = False
            flash('An invalid category ID was provided.')

    # Test: Image URL is valid and meets our requirements
    if instrument['image'] is not None:
        validated_url, image_is_valid = validate_image_url(instrument['image'])

        instrument['image'] = validated_url
        is_valid = is_valid and image_is_valid

    return instrument, is_valid
