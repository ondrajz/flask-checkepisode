from checkepisode import app
from flask import session, request, redirect, url_for, g, render_template, \
        flash, jsonify, abort, make_response
from sqlalchemy.orm.exc import NoResultFound
from functools import wraps
from flask.ext.security import Security, LoginForm, RegisterForm

@app.route("/login")
def login():
    return render_template('login.html', form=LoginForm())
    
@app.route("/register")
def register():
    return render_template('register.html', form=RegisterForm())
