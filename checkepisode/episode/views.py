from checkepisode.episode import Episode
from checkepisode.series import UserSerie
from checkepisode import app, db, create_token, validate_token
from flask.ext.security import login_required, current_user
from flask import (
    request,
    render_template,
    redirect,
    url_for,
    flash,
)
from datetime import datetime


@app.route('/episode/<int:id>')
def showEpisode(id):
    create_token()
    episode = Episode.query.get_or_404(id)
    return render_template('episode/detail.html', episode=episode)


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
        if episode in current_user.watched_episodes:
            current_user.watched_episodes.remove(episode)
            flash('Removed from watched!', 'success')

    fav = UserSerie.query.\
        filter_by(user=current_user, \
        serie=episode.serie).first()
    if fav is not None:
        fav.last_watched = datetime.now()
        db.session.add(fav)

    db.session.commit()

    if url is not None:
        return redirect(url)

    return redirect(url_for('showEpisode', id=episode.id))
