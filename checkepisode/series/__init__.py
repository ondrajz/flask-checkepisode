from checkepisode import db
from datetime import datetime


class Language(db.Model):
    __tablename__ = 'language'
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(2), unique=True, nullable=False)

    def __init__(self, caption):
        self.caption = caption

    def __repr__(self):
        return '<Language %r>' % self.caption


class Network(db.Model):
    __tablename__ = 'network'
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(40), unique=True, nullable=False)

    def __init__(self, caption):
        self.caption = caption

    def __repr__(self):
        return '<Network %r>' % self.caption


class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(20), unique=True, nullable=False)
    display = db.Column(db.String(20), unique=True, nullable=False)

    def __init__(self, caption):
        self.caption = caption
        self.display = caption

    def __repr__(self):
        return '<Status %r>' % self.caption

series_genres = db.Table('series_genres',
    db.Column('series_id', db.Integer, db.ForeignKey('serie.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'))
)


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(40), unique=True, nullable=False)

    def __init__(self, caption):
        self.caption = caption

    def __repr__(self):
        return '<Genre %r>' % self.caption


class Serie(db.Model):
    __tablename__ = 'serie'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    tvdb_id = db.Column(db.Integer, unique=True)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    language = db.relationship('Language',
        backref=db.backref('series', lazy='dynamic'))
    first_aired = db.Column(db.String(8))
    airs_dow = db.Column(db.String(2))
    airs_time = db.Column(db.String(7))
    genre = db.relationship('Genre', secondary=series_genres,
        backref=db.backref('series', lazy='dynamic'))
    imdb_id = db.Column(db.String(10))
    network_id = db.Column(db.Integer, db.ForeignKey('network.id'))
    network = db.relationship('Network',
        backref=db.backref('series', lazy='dynamic'))
    overview = db.Column(db.Text)
    tvdb_rating = db.Column(db.Float)
    tvdb_ratecount = db.Column(db.Integer)
    runtime = db.Column(db.Integer)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    status = db.relationship('Status',
        backref=db.backref('series', lazy='dynamic'))
    last_update = db.Column(db.Integer)
    banner = db.Column(db.String(40))
    poster = db.Column(db.String(40))

    def __init__(self, name, tvdb_id):
        self.name = name
        self.tvdb_id = tvdb_id

    def __repr__(self):
        return '<Serie %s>' % self.name


class UserSerie(db.Model):
    __tablename__ = 'user_series'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), \
        primary_key=True)
    serie_id = db.Column(db.Integer, db.ForeignKey('serie.id'), \
        primary_key=True)
    last_watched = db.Column(db.DateTime)
    user = db.relationship("User", \
        backref=db.backref("user_series", cascade="all, delete-orphan"))
    serie = db.relationship("Serie")

    def __init__(self, serie=None, user=None):
        self.user = user
        self.serie = serie
        self.last_watched = datetime.now()

import views
