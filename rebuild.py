from checkepisode.models import db,Series
db.drop_all()
db.create_all()

shows = open('shows','r')
for line in shows.readlines():
    show = line.strip('\n').split(',')
    if len(show)>=2 and len(show[0])>0 and len(show[1])>0:
        tvName = show[0]
        tvId = show[1]
        print '%s [%s]' % (tvName, tvId)
        new = Series(tvName, tvId)
        db.session.add(new)
shows.close()

db.session.commit()

ser = []
ser.append(Series.query.get(1))
ser.append(Series.query.get(16))
ser.append(Series.query.get(8))
ser.append(Series.query.get(3))
ser.append(Series.query.get(12))
#admin.favorite_series = ser

db.session.commit()