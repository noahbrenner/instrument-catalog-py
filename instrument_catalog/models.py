from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(16384), nullable=False)


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
    category = db.relationship('Category', lazy=True,
                               backref=db.backref('instruments', lazy=True,
                                                  order_by='Instrument.name'))

    alternate_names = db.relationship('AlternateInstrumentName', lazy=False,
                                      order_by='AlternateInstrumentName.index')
