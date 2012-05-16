from checkepisode.models import db,Series
db.drop_all()
db.create_all()

shows = open('shows','r')
for line in shows.readlines():
    tvName = line.strip('\n')
    if len(tvName)>0:
        print '%s' % tvName
        new = Series(tvName)
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