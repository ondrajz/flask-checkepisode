from checkepisode.episode import Episode
from checkepisode.series import Serie
from checkepisode import app, db, create_token, validate_token
from flask.ext.security import login_required, current_user
from flask import (
    request,
    render_template,
    redirect,
    url_for,
    flash,
)
from sqlalchemy.sql import func
from datetime import date

today = date.today()


@app.route('/series/<int:id>')
def showSeries(id):
    create_token()
    series = Serie.query.get_or_404(id)
    try:
        seasonCount = int(db.session.query(func.max(Episode.seas_num)).\
            filter(Episode.serie == series).scalar())
    except:
        seasonCount = 0
    season = int(request.args.get('season', seasonCount))
    season_list = Episode.query.filter_by(serie=series, seas_num=season).all()
    if not series.last_update:
        flash('This show does not contain all informations. \
            It will be updated soon.', 'warning')
    return render_template('series/detail.html', series=series, \
        seasonCount=seasonCount, season=season, season_list=season_list, \
        today=today.strftime('%Y%m%d'))


@app.route('/series/<int:id>/check', methods=('GET', 'POST'))
@login_required
def checkSeries(id):
    series = Serie.query.get_or_404(id)

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
