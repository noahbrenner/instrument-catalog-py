"""
instrument_catalog.db_init
~~~~~~~~~~~~~~~~~~~~~~~~~~

Initializes predefined rows in the application's database.  This module
should be run only once, after creating a fresh database.  There is no
check to verify whether the database or these predefined rows already
exist, so such a check should be performed before running this code.
"""
import itertools
from .models import db, User, Category, Instrument, AlternateInstrumentName


def init():
    """Initialize rows in the database.

    The IDs for each row are hard-coded so that other rows created here can
    reference those IDs before committing to the database (the only
    exception is for AlternateInstrumentName rows, which don't have an ID
    column).  While this hard coding could be avoided by using multiple
    commits, we want to avoid that approach in order to create a single,
    atomic commit.
    """
    # === Create users ===

    idx = itertools.count(0)  # Counter for generating IDs
    user1 = User(name='Admin1', id=next(idx), email='fake@example.com')
    user2 = User(name='Admin2', id=next(idx), email='madeup@example.com')
    db.session.add(user1)
    db.session.add(user2)

    # === Create categories ===

    idx = itertools.count(0)  # Create new counter
    strings = Category(name='Strings', id=next(idx), description=(
        'Instruments which create sound through the vibration of tensioned'
        ' strings. The strings may be set in motion in various ways, including'
        ' plucking, striking, bowing, or even wind.'))

    winds = Category(name='Winds', id=next(idx), description=(
        'Winds description'))

    percussion = Category(name='Percussion', id=next(idx), description=(
        'Percussion description'))

    for category in (strings, winds, percussion):
        db.session.add(category)

    # === Create instruments ===

    idx = itertools.count(0)  # Create new counter
    pedal_harp = Instrument(
        name='Pedal Harp', id=next(idx), image='pedalharp.jpg',
        category_id=strings.id, user_id=user1.id, description=(
            'Pedal harps generally have 48 strings which are plucked with the'
            ' fingers. The strings are tuned to a diatonic scale, but the set'
            ' of notes can be quickly changed by using the pedals.\n\nThe'
            ' instrument has 7 pedals, each of which controls the pitch of'
            ' one note name (every octave of a single note note, such as C).'))

    lever_harp = Instrument(
        name='Lever Harp', id=next(idx), image='leverharp.jpg',
        category_id=strings.id, user_id=user2.id, description=(
            'it’s another type of harp!'))

    flute = Instrument(
        name='Flute', id=next(idx), image='flute.jpg',
        category_id=winds.id, user_id=user1.id, description=(
            'You blow across it and make noise.'))

    for instrument in (pedal_harp, lever_harp, flute):
        db.session.add(instrument)

    # === Create alternate instrument names ===

    alternate_names = [
        (pedal_harp, ['Concert Harp', 'Orchestral Harp']),
        (lever_harp, ['Celtic Harp', 'Folk Harp']),
    ]

    for instrument, names in alternate_names:
        for index, alt_name in enumerate(names):
            db.session.add(AlternateInstrumentName(
                instrument_id=instrument.id, name=alt_name, index=index))

    # === Commit changes ===

    db.session.commit()
