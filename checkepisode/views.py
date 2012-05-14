from checkepisode import app, create_token, validate_token
from checkepisode.models import *
from flask import abort, render_template, request, redirect, \
    url_for, g, flash, session, abort
from datetime import date, timedelta, datetime
import urllib
from sqlalchemy.sql import func, tuple_, or_
from checkepisode.login import login_required

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
    t = date.today() - timedelta(days=7)
    if g.user:
        sids = [x.id for x in g.user.favorite_series]
        episodes = Episode.query.filter(Episode.series_id.in_(sids)).filter(Episode.air_time>=t.strftime('%Y%m%d')).order_by(Episode.air_time)
        return render_template('watchlist.html', episodes=episodes, today=today.strftime('%Y%m%d'))
    else:
        episodes = Episode.query.filter(Episode.air_time>=t.strftime('%Y%m%d')).order_by(Episode.air_time)
        return render_template('home.html', episodes=episodes, today=today.strftime('%Y%m%d'))
    
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
    
@app.route('/series/<int:id>/add', methods=('GET', 'POST'))
@login_required
def addSeries(id):
    series = Series.query.get_or_404(id)
    
    if request.method == 'GET':
        create_token()
        return render_template('series/add.html', series=series)
    
    if not validate_token():
        return redirect(url_for('addSeries', id=series.id))
    
    add = request.form.get('add', None)
    if add:
        if series not in g.user.favorite_series:
            g.user.favorite_series.append(series)
            flash('Added to watchlist!', 'success')
    else:
        g.user.favorite_series.remove(series)
        flash('Removed from watchlist!', 'success')
    db.session.commit()
    
    return redirect(url_for('showSeries', id=series.id))