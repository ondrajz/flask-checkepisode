from checkepisode import db
from datetime import datetime


class Episode(db.Model):
    __tablename__ = 'episode'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90))
    tvdb_id = db.Column(db.Integer, unique=True, nullable=False)
    serie_id = db.Column(db.Integer, db.ForeignKey('serie.id'))
    air_time = db.Column(db.String(8))
    seas_num = db.Column(db.Integer)
    epis_num = db.Column(db.Integer)
    overview = db.Column(db.Text)
    tvdb_rating = db.Column(db.Float)
    tvdb_ratecount = db.Column(db.Integer)
    last_update = db.Column(db.Integer)
    graphic = db.Column(db.String(40))

    serie = db.relationship('Serie',
        backref=db.backref('episodes', lazy='dynamic'))

    def __init__(self, epID):
        self.tvdb_id = epID

    def __repr__(self):
        return u'<Episode %d>' % self.tvdb_id

    @property
    def runtime(self):
        if not isinstance(self.air_time, unicode):
            return self.air_time
        t = self.serie.airs_time
        if t is None:
            t = '12:00AM'
        try:
            d = datetime.strptime('%s %s' % (self.air_time, t), \
                '%Y%m%d %I:%M%p')
        except:
            try:
                d = datetime.strptime('%s %s' % (self.air_time, t), \
                    '%Y%m%d %H:%M')
            except:
                d = None
        return d

    @property
    def represent(self):
        return u'S%02dE%02d' % (self.seas_num, self.epis_num)

    @property
    def aired(self):
        if self.runtime is None:
            return False
        if self.runtime < datetime.now():
            return True
        return False

import views
