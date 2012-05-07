from checkepisode import app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

"""class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    #password = db.Column(db.String(128), unique=False)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username"""
        
class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(2), unique=True, nullable=False)

    def __init__(self, caption):
        self.caption = caption

    def __repr__(self):
        return '<Language %r>' % self.caption
        
genres = db.Table('genres',
    db.Column('series_id', db.Integer, db.ForeignKey('series.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'))
)
        
class Network(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(40), unique=True, nullable=False)

    def __init__(self, caption):
        self.caption = caption

    def __repr__(self):
        return '<Network %r>' % self.caption
        
class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(40), unique=True, nullable=False)

    def __init__(self, caption):
        self.caption = caption

    def __repr__(self):
        return '<Genre %r>' % self.caption
    
class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(20), unique=True, nullable=False)

    def __init__(self, caption):
        self.caption = caption

    def __repr__(self):
        return '<Status %r>' % self.caption
        
class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    tvdb_id = db.Column(db.Integer, unique=True)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    language = db.relationship('Language',
        backref=db.backref('series', lazy='dynamic'))
    first_aired = db.Column(db.String(8))
    airs_dow = db.Column(db.String(2))
    airs_time = db.Column(db.String(7))
    #genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    genre = db.relationship('Genre', secondary=genres,
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

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Series %s>' % self.name
        
    """@property
    def first_aired(self):
        if not isinstance(self._first_aired, unicode):
            return self._first_aired
        return datetime.strptime(self._first_aired, '%Y-%m-%d %H:%M:%S.%f')"""
        
class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90))
    tvdb_id = db.Column(db.Integer, unique=True, nullable=False)
    #tvdb_series_id = dbColumn(db.Integeger, nullable=False)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'))
    series = db.relationship('Series',
        backref=db.backref('episodes', lazy='dynamic'))
    air_time = db.Column(db.String(8))
    seas_num = db.Column(db.Integer)
    epis_num = db.Column(db.Integer)
    overview = db.Column(db.Text)
    tvdb_rating = db.Column(db.Float)
    tvdb_ratecount = db.Column(db.Integer)
    last_update = db.Column(db.Integer)

    def __init__(self, epID):
        self.tvdb_id = epID

    def __repr__(self):
        return '<Episode %r(%d)>' % self.name,self.tvdb_id
        
    """@property
    def air_time(self):
        if not isinstance(self._air_time, unicode):
            return self._air_time
        return datetime.strptime(self._air_time, '%Y-%m-%d %H:%M:%S.%f')"""