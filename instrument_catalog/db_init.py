"""
instrument_catalog.db_init
~~~~~~~~~~~~~~~~~~~~~~~~~~

Initializes predefined rows in the application's database.  This module
should be run only once, after creating a fresh database.  There is no
check to verify whether the database or these predefined rows already
exist, so such a check should be performed before running this code.
"""
from textwrap import dedent
from .models import db, User, Category, Instrument, AlternateInstrumentName


def init(in_prod_environment=True):
    """Initialize rows in the database.

    The IDs for each row are hard-coded so that other rows created here can
    reference those IDs before committing to the database (the only
    exception is for AlternateInstrumentName rows, which don't have an ID
    column).  While this hard coding could be avoided by using multiple
    commits, we want to avoid that approach in order to create a single,
    atomic commit.
    """
    # === Create users ===

    user1 = User(name='Admin1', email='fake@example.com')
    db.session.add(user1)

    if in_prod_environment:
        print('Initiating database rows in PRODUCTION environment')
        # Associate all generated rows with the same admin user
        user2 = user1
    else:
        print('Initiating database rows in DEVELOPMENT environment')
        # Create an additional user to help with testing permissions
        user2 = User(name='Admin2', email='madeup@example.com')
        db.session.add(user2)

    # === Create categories ===

    strings = Category(name='Strings', description=dedent("""\
        Instruments which create sound through the vibration of tensioned
        strings. The strings may be set in motion in various ways, including
        plucking, striking, bowing, or even wind."""))

    winds = Category(name='Winds', description=dedent("""\
        'Winds description"""))

    percussion = Category(name='Percussion', description=dedent("""\
        'Percussion description"""))

    db.session.add_all([strings, winds, percussion])

    # === Create instruments ===

    pedal_harp = Instrument(
        name='Pedal Harp', image='pedalharp.jpg',
        category=strings, user=user1, description=dedent("""\
            Pedal harps generally have 48 strings which are plucked with the
            fingers. The strings are tuned to a diatonic scale, but the set of
            notes can be quickly changed by using the pedals.

            The instrument has 7 pedals, each of which controls the pitch of
            one note name (every octave of a single note note, such as C)."""))

    lever_harp = Instrument(
        name='Lever Harp', image='leverharp.jpg',
        category=strings, user=user2, description=dedent("""\
            It's another type of harp!"""))

    flute = Instrument(
        name='Flute', image='flute.jpg',
        category=winds, user=user1, description=dedent("""\
            You blow across it and make noise."""))

    # === Create alternate instrument names ===

    alternate_names = [
        (pedal_harp, ['Concert Harp', 'Orchestral Harp']),
        (lever_harp, ['Celtic Harp', 'Folk Harp']),
    ]

    for instrument, names in alternate_names:
        instrument.alternate_names.extend(
            AlternateInstrumentName(name=name, index=index)
            for index, name in enumerate(names))

    # === Commit changes ===

    db.session.commit()
