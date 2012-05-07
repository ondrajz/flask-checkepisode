from checkepisode import app
from checkepisode.models import *
from flask import abort, render_template, request, redirect, \
    url_for, g, flash, session
from datetime import date

today = date.today()

@app.route('/')
def hello():
    episodes = Episode.query.filter(Episode.air_time>today.strftime("%Y%m%d")).order_by(Episode.air_time)
    return render_template('home.html', episodes=episodes)
    
@app.route('/series/<int:id>')
def showSeries(id):
    series = Series.query.get_or_404(id)
    return render_template('series/series.html', series=series)