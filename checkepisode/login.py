from flask import session, request, redirect, url_for, g, render_template, \
        flash, jsonify, abort
from checkepisode import app
from checkepisode.models import *
from sqlalchemy.orm.exc import NoResultFound
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.errorhandler(403)
def require_login(error):
    if g.json:
        return jsonify(status='error',
                        message='You need to be logged in to do that.')
    session['redirect-to'] = request.url
    flash('You need to be logged in to view that content.', 'error')
    return redirect(url_for('login'))

@app.before_request
def load_user():
    g.user = None
    if 'user-id' in session:
        try:
            g.user = User.query.filter_by(id=session['user-id']).one()
        except db.NoResultFound:
            app.logger.error("Session's user id \"%s\" does not exist",
                    session['user-id'])

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'GET':
        if 'redirect-to' in session:
            return render_template('login.html'), 403
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']

    try:
        user = User.query.filter_by(name=username).one()
    except NoResultFound:
        flash('Invalid username or password.', 'error')
        app.logger.info('Trying to log in with nonexisting user: %s',
                username)
        return redirect(url_for('login'))

    if not user.verify(password):
        flash('Invalid username or password.', 'error')
        app.logger.info('Login for %s (%d) failed.', user.name, user.id)
        return redirect(url_for('login'))

    url = session.pop('redirect-to', url_for('index'))
    session['user-id'] = user.id
    app.logger.info('User %s (%d) logged in successfully.',
            user.name, user.id)
    flash('You have logged in.', 'success')
    return redirect(url)

@app.route('/logout')
def logout():
    session.pop('user-id', None)
    flash('You have logged out.', 'success')
    return redirect(url_for('index'))