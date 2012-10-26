from flaskext.script import Manager
from checkepisode import app, db
from checkepisode.series import Serie
from checkepisode.users import Role
import checkepisode

manager = Manager(app)


@manager.command
def dropdb():
    db.drop_all()


@manager.command
def createdb():
    db.create_all()


@manager.command
def addroles():
    a = Role(name='admin')
    u = Role(name='user')
    db.session.add(a)
    db.session.add(u)
    db.session.commit()


@manager.command
def filltv():
    shows = open('shows', 'r')
    for line in shows.readlines():
        show = line.strip('\n').split(',')
        if len(show) >= 2 and len(show[0]) > 0 and len(show[1]) > 0:
            tvName = show[0]
            tvId = show[1]
            print 'adding %s [%s]' % (tvName, tvId)
            new = Serie(tvName, tvId)
            db.session.add(new)
    shows.close()
    db.session.commit()


@manager.command
def runserver():
    checkepisode.run()


@manager.command
def cleartv():
    for s in Serie.query:
        print 'clearing %s [%s]' % (s.name, s.tvdb_id)
        s.last_update = None
    db.session.commit()

if __name__ == "__main__":
    manager.run()
