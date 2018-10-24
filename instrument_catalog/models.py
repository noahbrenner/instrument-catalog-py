from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeSerializer, BadData


db = SQLAlchemy()
serializer = None  # Will hold an instance of URLSafeSerializer


def get_serializer():
    """Returns an instance or URLSafeSerializer."""
    global serializer

    # We need access to our app's secret key to create the serializer, but we
    # don't have access to `current_app` in global scope (we're not in an app
    # context), so we'll instantiate the serializer inside this function, which
    # can be called once we *are* in an app context. We'll cache the serializer
    # in global scope so that we don't create a new instance on each call.
    serializer = serializer or URLSafeSerializer(
            secret_key=current_app.secret_key,
            signer_kwargs={'key_derivation': 'hmac'})

    return serializer


class User(db.Model):
    __table_args__ = (
        db.UniqueConstraint('oauth_provider', 'provider_user_id',
                            name='unique_oauth_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    oauth_provider = db.Column(db.String(128))
    provider_user_id = db.Column(db.String)
    access_token = db.Column(db.String)

    # Properties and methods used by flask-login

    is_authenticated = True  # flask-login only sees this after authentication
    is_active = True  # We have not yet implemented deactivation of accounts
    is_anonymous = False

    def get_id(self):
        """Return a Unicode representation of the user ID."""
        return str(self.id)

    # Methods related to API keys

    def get_api_key(self):
        """Return an API key (a signed user ID)."""
        # TODO Improve this naive implementation by generating random API keys
        # and storing them in encrypted form. Also allow for invalidating keys
        # and generating new ones.
        serializer = get_serializer()
        return serializer.dumps(self.id)

    @staticmethod
    def verify_api_key(api_key):
        """Return `api_key`'s associated user ID or None."""
        serializer = get_serializer()

        try:
            return int(serializer.loads(api_key))
        except (BadData, ValueError):
            return None


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(16384), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class AlternateInstrumentName(db.Model):
    __table_args__ = (
        # Each name has a unique sort order for a given instrument
        db.UniqueConstraint('instrument_id', 'index',
                            name='unique_instrument_index'),
    )

    instrument_id = db.Column(db.Integer,
                              db.ForeignKey('instrument.id'), primary_key=True)
    name = db.Column(db.String(128), primary_key=True)
    index = db.Column(db.SmallInteger)  # Used for display ordering


class Instrument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(16384), nullable=False)
    image = db.Column(db.String(512))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),
                            nullable=False)

    user = db.relationship('User', lazy=True)

    category = db.relationship('Category', lazy=True,
                               backref=db.backref('instruments', lazy=True,
                                                  order_by='Instrument.name'))

    alternate_names = db.relationship('AlternateInstrumentName', lazy=False,
                                      order_by='AlternateInstrumentName.index',
                                      cascade='all, delete-orphan')

    def get_image_url(self):
        """Return the instrument's image URL or a fallback placeholder."""
        return self.image or '/static/logo.svg'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image': self.image,
            'category_id': self.category_id,
            'alternate_names': [alt.name for alt in self.alternate_names]
        }
