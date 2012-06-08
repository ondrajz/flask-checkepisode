from checkepisode.models import db, Serie
import sys


def printOptions():
    print "Options: \n\t" \
        "'drop' - drop all\n\t" \
        "'create' - create all\n\t" \
        "'fill' - fill with series\n\t" \
        "'clear' - clears series lastupdate"

if len(sys.argv) > 1:
    if sys.argv[1] == 'drop':
        db.drop_all()
    elif sys.argv[1] == 'create':
        db.create_all()
    elif sys.argv[1] == 'fill':
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
    elif sys.argv[1] == 'clear':
        for s in Serie.query:
            print 'clearing %s [%s]' % (s.name, s.tvdb_id)
            s.last_update = None
        db.session.commit()
    else:
        printOptions()
else:
    printOptions()
