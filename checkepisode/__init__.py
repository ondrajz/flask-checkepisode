from flask import Flask, flash, request, session, render_template, g, jsonify, current_app
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security
from flask.ext.security.datastore import SQLAlchemyUserDatastore
import os

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = app.config['SECRET_KEY']

db = SQLAlchemy(app)
from models import User, Role
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

import models
import friendly_time
import login
import views
import logger

@app.before_first_request
def before_first_request():
    if User.query.count() == 0:
        current_app.security.datastore.create_role(name='admin')
        current_app.security.datastore.create_role(name='user')
        current_app.security.datastore.create_user(name='admin', email='admin@admin.com',
                                                    password='admin', roles=['admin'])

@app.before_request
def load_json():
    g.json = request.is_xhr

def run():
    app.debug=app.config['DEBUG']
    app.run(host=app.config['HOST'], port=app.config['PORT'])
