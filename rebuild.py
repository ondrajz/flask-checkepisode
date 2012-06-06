from checkepisode.models import db, Series
import sys


def printOptions():
    print "Options: \n\t" \
        "'all' - rebuild whole database\n\t" \
        "'clear' - clears series lastupdate"

if len(sys.argv) > 1:
    if sys.argv[1] == 'all':
        db.drop_all()
        db.create_all()

        shows = open('shows', 'r')
        for line in shows.readlines():
            show = line.strip('\n').split(',')
            if len(show) >= 2 and len(show[0]) > 0 and len(show[1]) > 0:
                tvName = show[0]
                tvId = show[1]
                print 'adding %s [%s]' % (tvName, tvId)
                new = Series(tvName, tvId)
                db.session.add(new)
        shows.close()

        db.session.commit()
    elif sys.argv[1] == 'clear':
        for s in Series.query:
            print 'clearing %s [%s]' % (s.name, s.tvdb_id)
            s.last_update = None
        db.session.commit()
    else:
        printOptions()
else:
    printOptions()
