from checkepisode import app
from checkepisode.models import *
from flask.ext.sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context

favorite_series = db.Table('favorite_series',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('series_id', db.Integer, db.ForeignKey('series.id'))
)

watched_episodes = db.Table('watched_episodes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('episode_id', db.Integer, db.ForeignKey('episode.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35), unique=True)
    password = db.Column(db.String(128))
    favorite_series = db.relationship('Series', secondary=favorite_series,
        backref=db.backref('users', lazy='dynamic'))
    watched_episodes = db.relationship('Episode', secondary=watched_episodes,
        backref=db.backref('users', lazy='dynamic'))

    def __init__(self, name, password):
        app.logger.info('Creating user "%s".', name)
        self.name = name
        self.password = pwd_context.encrypt(password)

    def verify(self, password):
        return pwd_context.verify(password, self.password)