"""
instrument_catalog.db_init
~~~~~~~~~~~~~~~~~~~~~~~~~~

Initializes predefined rows in the application's database.  This module
should be run only once, after creating a fresh database.  There is no
check to verify whether the database or these predefined rows already
exist, so such a check should be performed before running this code.
"""
from textwrap import dedent
import flask
from .models import db, User, Category, Instrument, AlternateInstrumentName


def init():
    """Initialize rows in the database."""

    # === Create users ===

    user1 = User(name='Admin1')
    db.session.add(user1)

    if flask.current_app.env == 'production':
        # Associate all generated rows with the same admin user
        user2 = user1
    else:
        # Create an additional user to help with testing permissions
        user2 = User(name='Admin2')
        db.session.add(user2)

    print('Creating database rows in {env} environment.'
          .format(env=flask.current_app.env.upper()))

    # === Create categories ===

    strings = Category(name='Strings', description=dedent("""\
        Instruments which create sound through the vibration of tensioned
        strings. The strings may be set in motion in various ways, including
        plucking, striking, bowing, or even wind."""))

    winds = Category(name='Winds', description=dedent("""\
        Instruments which create sound through the vibration of air columns.
        The vibration may be initiated in various ways, including by the
        player's breath directly, via a vibrating reed, or even
        mechanically-generated airflow."""))

    percussion = Category(name='Percussion', description=dedent("""\
        Instruments which create sound by striking or being struck. Some
        percussion instruments are tuned to specific pitches, while others are
        not."""))

    electronic = Category(name='Electronic', description=dedent("""\
        Instruments which create sound electronically, rather than
        acoustically."""))

    db.session.add_all([strings, winds, percussion, electronic])

    # === Create instruments ===

    # These are implicitly added to the session via their category association

    pedal_harp = Instrument(
        name='Pedal Harp',
        image=('https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/'
               'Harp.svg/220px-Harp.svg.png'),
        category=strings, user=user1, description=dedent("""\
            Pedal harps generally have 48 strings which are plucked with the
            fingers. The strings are tuned to a diatonic scale, but the set of
            notes can be quickly changed by using the pedals.

            The instrument has 7 pedals, each of which controls the pitch of
            one note name (every octave of a single note note, such as C)."""))

    lever_harp = Instrument(
        name='Lever Harp',
        image=('https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/'
               'Harpe_celtique_moderne_%28Camac%29.jpg/'
               '360px-Harpe_celtique_moderne_%28Camac%29.jpg'),
        category=strings, user=user2, description=dedent("""\
            Lever harps are generally tuned to a [diatonic][] scale. They have
            a small lever at the top of each string which can be engaged to
            raise the pitch by a half step. This allows for playing accidentals
            and playing in different keys.

            [diatonic]: https://en.wikipedia.org/wiki/Diatonic_scale"""))

    flute = Instrument(
        name='Flute',
        image=('https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/'
               'Western_concert_flute_%28Yamaha%29.jpg/'
               '441px-Western_concert_flute_%28Yamaha%29.jpg'),
        category=winds, user=user1, description=dedent("""\
            Flutes are played by blowing across a hole near the closed end of
            the instrument. The pitch is controlled by closing various
            combinations of other holes along the length of the flute, which
            effectively changes the length of the vibrating air column."""))

    tambourine = Instrument(
        name='Tambourine',
        image=('https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/'
               'Riqq.jpg/309px-Riqq.jpg'),
        category=percussion, user=user2, description=dedent("""\
            Tambourines are very short cylinders with pairs of small, metal
            disks at several points around its perimeter which jingle when the
            instrument is struck. Some also have a drumhead covering one of the
            open sides of the cylinder. There are tambourines from many parts
            of the world and they have many different names."""))

    theramin = Instrument(
        name='Theremin',
        image=('https://upload.wikimedia.org/wikipedia/commons/c/c5/'
               'Lydia_kavina.jpg'),
        category=electronic, user=user1, description=dedent("""\
            A theremin is played without actually touching the instrument. It
            has two antennas, one vertical, one horizontal. The proximity of
            the players hand to one antenna controls the pitch, while the other
            antenna similarly controls the volume."""))

    # === Create alternate instrument names ===

    # These are implicitly added to the session via their instruments

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
