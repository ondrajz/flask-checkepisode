from checkepisode import app, create_token, validate_token
from checkepisode.models import *
from flask import abort, render_template, request, redirect, \
    url_for, flash
from datetime import date, timedelta, datetime
import urllib
from sqlalchemy.sql import func
from flask.ext.security import login_required, current_user
from search import searchFor

today = date.today()


@app.template_filter()
def safe_url(url):
    return urllib.quote(url)


@app.template_filter()
def to_date(dt):
    try:
        res_dt = datetime.strptime(dt.replace('-', ''), '%Y%m%d')
    except:
        return None
    return res_dt


@app.context_processor
def utility_processor():
    def pad_zeroes(number):
        return u'%02d' % number
    return dict(pad_zeroes=pad_zeroes)


@app.context_processor
def utility_processor():
    def date_string(date):
        if date is None:
            return "Unknown"
        return date.strftime('%a %Y-%m-%d %H:%M')
    return dict(date_string=date_string)


@app.context_processor
def utility_processor():
    def date_string_my(date):
        if date is None:
            return "Unknown"
        return date.strftime('%B %d, %Y')
    return dict(date_string_my=date_string_my)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.route('/')
def index():
    if current_user.is_authenticated():
        return redirect(url_for('watchlist'))
    t = date.today() - timedelta(days=7)
    episodes = Episode.query.filter(Episode.air_time >= t.strftime('%Y%m%d'))\
        .order_by(Episode.air_time)
    return render_template('home.html', episodes=episodes, \
        today=datetime.now())


@app.route('/watchlist')
@login_required
def watchlist():
    create_token()
    episodes = Episode.query.filter(Episode.series_id.in_( \
        x.id for x in current_user.favorite_series)).\
        filter(Episode.air_time != None).order_by(Episode.air_time)
    if episodes.count() <= 0:
        flash('You have no shows in your watchlist! \
            Add some of the popular ones or use search!', 'warning')
        return redirect(url_for('hotShows'))
    aired_eps = []
    upcoming_eps = []
    for e in episodes:
        if e.runtime < datetime.now():
            aired_eps.append(e)
        else:
            upcoming_eps.append(e)
    return render_template('watchlist.html', aired_eps=aired_eps, \
        upcoming_eps=upcoming_eps, today=datetime.now())


@app.route('/series/<int:id>')
def showSeries(id):
    create_token()
    series = Series.query.get_or_404(id)
    try:
        seasonCount = int(db.session.query(func.max(Episode.seas_num)).\
            filter(Episode.series == series).scalar())
    except:
        seasonCount = 0
    season = int(request.args.get('season', seasonCount))
    season_list = Episode.query.filter_by(series=series, seas_num=season).all()
    if not series.last_update:
        flash('This show does not contain all informations. \
            It will be updated soon.', 'warning')
    return render_template('series/detail.html', series=series, \
        seasonCount=seasonCount, season=season, season_list=season_list, \
        today=today.strftime('%Y%m%d'))


@app.route('/episode/<int:id>')
def showEpisode(id):
    create_token()
    episode = Episode.query.get_or_404(id)
    return render_template('episode/detail.html', episode=episode)


@app.route('/series/<int:id>/check', methods=('GET', 'POST'))
@login_required
def checkSeries(id):
    series = Series.query.get_or_404(id)

    if request.method == 'GET':
        return redirect(url_for('showSeries', id=series.id))

    url = request.referrer

    if not validate_token():
        return redirect(url_for('checkSeries', id=series.id))

    add = request.form.get('add', None)
    if add:
        if series not in current_user.favorite_series:
            current_user.favorite_series.append(series)
            flash('Added to watchlist!', 'success')
    else:
        current_user.favorite_series.remove(series)
        flash('Removed from watchlist!', 'success')
    db.session.commit()

    if url is not None:
        return redirect(url)

    return redirect(url_for('showSeries', id=series.id))


@app.route('/episode/<int:id>/check', methods=('GET', 'POST'))
@login_required
def checkEpisode(id):
    episode = Episode.query.get_or_404(id)

    if request.method == 'GET':
        return redirect(url_for('showEpisode', id=episode.id))

    url = request.referrer

    if not validate_token():
        return redirect(url_for('checkEpisode', id=episode.id))

    add = request.form.get('add', None)
    if add:
        if episode not in current_user.watched_episodes:
            current_user.watched_episodes.append(episode)
            flash('Added to watched!', 'success')
    else:
        current_user.watched_episodes.remove(episode)
        flash('Removed from watched!', 'success')
    db.session.commit()

    if url is not None:
        return redirect(url)

    return redirect(url_for('showEpisode', id=episode.id))


@app.route('/request', methods=['POST'])
@login_required
def addShow():
    tvdb_id = request.form.get('tvdb_id', None)
    name = request.form.get('name', None)
    first_aired = request.form.get('first_aired', None)
    overview = request.form.get('overview', None)

    if not validate_token():
        return abort(404)

    if tvdb_id is None or name is None:
        return abort(404)

    new = Series(name, tvdb_id)
    new.first_aired = first_aired.replace('-', '')
    new.overview = overview
    db.session.add(new)
    db.session.commit()

    try:
        id = new.id
    except:
        return abort(404)

    return redirect(url_for('showSeries', id=id))


@app.route('/search')
def search():
    create_token()
    q = request.args.get('q', None)
    series = ()
    found_series = ()
    if q is None:
        flash('Please add more constraints to your search!', 'warning')
    elif len(q) < 3:
        flash('Please enter at least 3 characters!', 'warning')
    else:
        series = Series.query.filter(Series.name.like(\
            ('%s%s%s' % ('%', q, '%')))).all()
        if current_user.is_authenticated():
            found_series = searchFor(q)[:10]
    return render_template('search.html', q=q, series=series, \
        found_series=found_series)


@app.route('/hot')
def hotShows():
    create_token()
    sub = db.session.query(favorite_series.c.series_id, func.count(\
        favorite_series.c.user_id).label('count')).group_by(\
        favorite_series.c.series_id).subquery()
    shows = db.session.query(Series, sub.c.count).outerjoin(\
        sub, Series.id == sub.c.series_id).order_by(db.desc('count'))
    return render_template('hot.html', shows=shows, today=datetime.now())
