from flask import Flask, flash, request, session, render_template, g, jsonify
import os

app = Flask(__name__)
app.config.from_object('real_config')
# this needs to be changed to config
app.secret_key = app.config['SECRET_KEY']

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

@app.before_request
def load_json():
    g.json = request.is_xhr

def run():
    app.debug=app.config['DEBUG']
    app.run(host=app.config['HOST'], port=app.config['PORT'])
