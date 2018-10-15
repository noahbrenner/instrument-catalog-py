from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __table_args__ = (
        db.UniqueConstraint('oauth_provider', 'provider_user_id',
                            name='unique_oauth_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    oauth_provider = db.Column(db.String(128))
    provider_user_id = db.Column(db.String)


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

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image': self.image,
            'category_id': self.category_id,
            'alternate_names': [alt.name for alt in self.alternate_names]
        }
