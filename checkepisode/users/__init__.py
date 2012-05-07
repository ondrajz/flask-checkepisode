from checkepisode import app
from checkepisode.models import *
from flask.ext.sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35), unique=True)
    password = db.Column(db.String(128))

    def __init__(self, name, password):
        app.logger.info('Creating user "%s".', name)
        self.name = name
        self.password = pwd_context.encrypt(password)

    def verify(self, password):
        return pwd_context.verify(password, self.password)