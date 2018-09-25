class obj():
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


CATEGORIES = [obj(id=idx, name=name, description='{} description'.format(name))
              for idx, name in enumerate(['Strings', 'Winds', 'Percussion'])]


INSTRUMENTS = [
    obj(id=0, name='Pedal Harp', category_id=0, category='Strings', user_id=0,
        image='pedalharp.jpg', alt_names=['Concert Harp', 'Orchestral Harp'],
        description=('Pedal harps generally have 48 strings which are plucked'
                     ' with the fingers. The strings are tuned to a diatonic'
                     ' scale, but the set of notes can be quickly changed by'
                     ' using the pedals.\n\nThe instrument has 7 pedals, each'
                     ' of which controlls the pitch of one note name (every'
                     ' octave of a single note note, such as C).')),
    obj(id=1, name='Lever Harp', category_id=0, category='Strings', user_id=1,
        image='leverharp.jpg', alt_names=['Celtic Harp', 'Folk Harp'],
        description='It\'s another type of harp!'),
    obj(id=2, name='Flute', category_id=1, category='Winds', user_id=2,
        image='flute.jpg', alt_names=[],
        description='You blow across it and make noise.')]


def get_categories():
    return CATEGORIES


def get_category(id):
    try:
        return CATEGORIES[id]
    except IndexError:
        return None


def get_instruments():
    return INSTRUMENTS


def get_instrument(id):
    try:
        return INSTRUMENTS[id]
    except IndexError:
        return None
