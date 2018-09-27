from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(10000), nullable=False)


class AlternateInstrumentNames(db.Model):
    __table_args__ = (
        # Alternate names must be unique relative to a given instrument
        db.UniqueConstraint('instrument_id', 'name', name='_instrument_name'),
        # Each name must have a unique sort order for a given instrument
        db.UniqueConstraint('instrument_id', 'index', name='_instrument_index')
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    index = db.Column(db.Integer)  # Used for display ordering

    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'),
                              nullable=False)


class Instrument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(10000), nullable=False)
    image = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),
                            nullable=False)
    category = db.relationship('Category', backref='instruments', lazy=True)

    alternate_names = db.relationship('AlternateInstrumentNames', lazy=False)

    def iter_alt_names(self):
        for alternate in self.alternate_names:
            yield alternate.name
