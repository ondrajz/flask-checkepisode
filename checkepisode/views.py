from checkepisode import app, create_token, validate_token
from checkepisode.models import *
from flask import abort, render_template, request, redirect, \
    url_for, g, flash, session, abort
from datetime import date, timedelta, datetime
import urllib
from sqlalchemy.sql import func
from flask.ext.security import Security, LoginForm,  login_required, \
                                roles_accepted, current_user
today = date.today()

@app.template_filter()
def safe_url(url):
    return urllib.quote(url)

@app.template_filter()
def to_date(dt):
    return datetime.strptime(dt, '%Y%m%d')

@app.context_processor
def utility_processor():
    def pad_zeroes(number):
        return u'%02d' % number
    return dict(pad_zeroes=pad_zeroes)
    
@app.context_processor
def utility_processor():
    def date_string(date):
        return date.strftime('%a %Y-%m-%d %H:%M')
    return dict(date_string=date_string)
    
@app.context_processor
def utility_processor():
    def date_string_my(date):
        return date.strftime('%B %Y')
    return dict(date_string_my=date_string_my)
    
@app.context_processor
def utility_processor():
    def epNum(sNum, eNum):
        try:
            s = int(sNum)
            e = int(eNum)
        except:
            return u'S%02sE%02s' % (sNum, eNum)
        return u'S%02dE%02d' % (s, e)
    return dict(epNum=epNum)

@app.route('/')
def index():
    create_token()
    if current_user.is_authenticated():
        episodes = Episode.query.filter(Episode.series_id.in_(x.id for x in current_user.favorite_series)).filter(Episode.air_time!=None).order_by(Episode.air_time)
        aired_eps = []
        upcoming_eps = []
        for e in episodes:
            if e.runtime<datetime.now():
                aired_eps.append(e)
            else:
                upcoming_eps.append(e)
        return render_template('watchlist.html', aired_eps=aired_eps, upcoming_eps=upcoming_eps, today=datetime.now())
    else:
        t = date.today() - timedelta(days=7)
        episodes = Episode.query.filter(Episode.air_time>=t.strftime('%Y%m%d')).order_by(Episode.air_time)
        return render_template('home.html', episodes=episodes, today=datetime.now())
    
@app.route('/series/<int:id>')
def showSeries(id):
    create_token()
    series = Series.query.get_or_404(id)
    seasonCount = db.session.query(func.max(Episode.seas_num)).filter(Episode.series==series).scalar()
    try:
        season = int(request.args.get('season', seasonCount))
    except:
        season = seasonCount
    season_list = Episode.query.filter_by(series=series, seas_num=season)
    return render_template('series/detail.html', series=series, seasonCount=seasonCount, season=season, season_list=season_list, today=today.strftime('%Y%m%d'))
    
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