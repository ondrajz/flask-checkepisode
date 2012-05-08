from checkepisode.models import db,Series,User
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

admin = User('admin', 'admin')
db.session.add(admin)

db.session.commit()