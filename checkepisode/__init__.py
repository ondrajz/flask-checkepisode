from flask import Flask, request, session, g
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security
from flask.ext.security.datastore import SQLAlchemyUserDatastore
import os

app = Flask(__name__)
app.config.from_object('checkepisode.settings.' +
    os.environ.get('CHECKEPISODE_ENVIRONMENT', 'development'))
app.secret_key = app.config['SECRET_KEY']

db = SQLAlchemy(app)
from users import User, Role
Security(app, SQLAlchemyUserDatastore(db, User, Role), registerable=False)

app.mail = Mail(app)


def create_token(length=32):
    # Take random bytes from os.urandom, turn them into hexadecimals, and join
    # the result to one string.
    t = ''.join(map(lambda x: '{0:02x}'.format(ord(x)), os.urandom(length)))
    session['token'] = t
    return t


def validate_token():
    if request.form['token'] != session.pop('token', None):
        app.logger.info('Token does not exist: %s', request.form['token'])
        return False
    return True

import users
import series
import episode
import friendly_time
import login
import views
import logger


@app.before_request
def load_json():
    g.json = request.is_xhr


def run():
    app.debug = app.config['DEBUG']
    app.run(host=app.config['HOST'], port=app.config['PORT'])
