from checkepisode import app
from checkepisode.models import *
from flask import abort, render_template, request, redirect, \
    url_for, g, flash, session
from datetime import date, timedelta, datetime
import urllib
from sqlalchemy.sql import func

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
        return date.strftime('%a %Y-%m-%d')
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
    t = date.today() - timedelta(days=7)
    episodes = Episode.query.filter(Episode.air_time>=t.strftime('%Y%m%d')).order_by(Episode.air_time)
    return render_template('home.html', episodes=episodes, today=today.strftime('%Y%m%d'))
    
@app.route('/series/<int:id>')
def showSeries(id):
    series = Series.query.get_or_404(id)
    seasCount = db.session.query(func.max(Episode.seas_num)).filter(Episode.series==series).scalar()
    last_season = Episode.query.filter_by(series=series, seas_num=seasCount)
    return render_template('series/detail.html', series=series, seasCount=seasCount, last_season=last_season, today=today.strftime('%Y%m%d'))
    
@app.route('/episode/<int:id>')
def showEpisode(id):
    episode = Episode.query.get_or_404(id)
    return render_template('episode/detail.html', episode=episode)