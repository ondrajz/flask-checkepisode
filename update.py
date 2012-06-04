from checkepisode.models import *
from updater import *
import os, sys
import urllib

def getSeriesXml(serID):
    if serID:
        filehandle = urllib.urlopen('%sapi/%s/series/%s/en.xml' % (MIRROR, API_KEY, serID))
        try:
            tvxml = et.fromstring(filehandle.read())
        except:
            print "Failed xml parsing of:\n%s" % filehandle.read()
            return None
        return tvxml.find('Series')
    return None

def getEpisodeXml(epID):
    if epID:
        filehandle = urllib.urlopen('%sapi/%s/episodes/%s/en.xml' % (MIRROR, API_KEY, epID))
        try:
            tvxml = et.fromstring(filehandle.read())
        except:
            print "Failed xml parsing of:\n%s" % filehandle.read()
            return None
        return tvxml.find('Episode')
    return None

updFile = open(LAST_UPDATE, 'r')
last_time = int(updFile.readline())
updFile.close()

print "Updating\nlast update = %s" % last_time
print "------------------------------------------------"
filehandle = urllib.urlopen('%sapi/Updates.php?type=all&time=%s' % (MIRROR, last_time))
tvxml = et.fromstring(filehandle.read())

new_update = tvxml.findtext("Time")
series_updates = tvxml.findall('Series')
episode_updates = tvxml.findall('Episode')

print "%d series updates\n%d episode updates" % (len(series_updates), len(episode_updates))

x = 1
print "------------------------------------------------"
print "Updating series"
for s in series_updates:
    print "%d/%d series id = %s" % (x, len(series_updates), s.text)
    series = Series.query.filter_by(tvdb_id=s.text).first()
    if series:
        updateSeries(series, getSeriesXml(s.text))
    x = x + 1

x = 1
print "------------------------------------------------"
print "Updating episodes"
for e in episode_updates:
    print "%d/%d episode id = %s" % (x, len(episode_updates), e.text)
    updateEpisode(getEpisodeXml(e.text))
    x = x + 1

print "\nUpdating finished\nupdate time = %s" % new_update
updFile = open(LAST_UPDATE, 'w+')
updFile.write(new_update)
updFile.close()
