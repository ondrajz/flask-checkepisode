from checkepisode.models import db,Series

shows = open('shows','r')
for line in shows.readlines():
    tvName = line.strip('\n')
    if len(tvName)>0:
        print '%s' % tvName
        new = Series(tvName)
        db.session.add(new)
db.session.commit()
shows.close()