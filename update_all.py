from checkepisode.models import *
from xml.etree import ElementTree as et
import urllib
import zipfile
import os
from updater import *

def getIdFor(name):
    print "Retrieving ID for %s" % name
    filehandle = urllib.urlopen("%sapi/GetSeries.php?seriesname=%s" % (MIRROR, urllib.quote(name)))
    xml = filehandle.read()
    try:
        tvxml = et.fromstring(xml)
        series = tvxml.find('Series')
        if series is not None:
            serName = series.findtext('SeriesName')
            if serName == name:
                sId = int(series.findtext('seriesid'))
                print "Found id = %d" % sId
                return sId
            else:
                print 'Id not found'
    except:
        print "Failed parsing id info: \n%s" % xml
    return None
    
def getInfoFile(ser_id):
    d = '%s/seriesZip' % os.getcwd()
    if not os.path.exists(d):
        print "Creating %s" % d
        os.makedirs(d)
    if ser_id:
        print "Checking zipfile for %s" % ser_id
        tvdbZip = "seriesZip/%s.zip" % ser_id
        folder = "seriesZip/%s" % ser_id
        info = "%s/en.xml" % folder
        if os.path.isfile(info) and REMOVE_OLD:
            print "Removing old files"
            if os.path.isfile(tvdbZip):
                print "Removing old zipfile from %s" % tvdbZip
                os.remove(tvdbZip)
            if os.path.exists(folder):
                print "Removing contents from %s" % folder
                for the_file in os.listdir(folder):
                    file_path = os.path.join(folder, the_file)
                    print "Removing %s" % file_path
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception, e:
                        print e
            else:
                os.makedirs(folder)
        if not os.path.isfile(info):
            print "Retrieving zipfile for %s" % ser_id
            urllib.urlretrieve('%sapi/%s/series/%d/all/en.zip' % (MIRROR, API_KEY, ser_id), tvdbZip)
            if os.path.isfile(tvdbZip):
                print "Extracting files from %s" % tvdbZip
                z = zipfile.ZipFile(tvdbZip, 'r')
                z.extractall(folder)
        else:
            print "found en.xml"
        return info
    
def getAllInfo(series):
    if series:
        print "\nRetrieving all info about %d" % series.tvdb_id
        info = getInfoFile(series.tvdb_id)
        if os.path.isfile(info):
            print "Parsing en.xml"
            tvxml = et.parse(info)
            xmlSeries = tvxml.find('Series')
            if xmlSeries is not None:
                updateSeries(series, xmlSeries)
            xmlEpisodes = tvxml.findall('Episode')
            print "\nFound %d episodes" % len(xmlEpisodes)
            for xmlEpisode in xmlEpisodes:
                updateEpisode(xmlEpisode)
        print "\nRetrieving info finished\n"

series = Series.query.all()
print "Checking %d series for missing id\n" % len(series)
for s in series:
    print "Checking %s" % s.name
    if not s.tvdb_id:
        print "------------------------------------------------"
        print "Missing ID"
        newId = getIdFor(s.name)
        if newId:
            print "Saving ID"
            s.tvdb_id = newId
            db.session.commit()
            getAllInfo(s)
            print "Committing to database.."
            db.session.commit()
        print "------------------------------------------------\n"
print "Checking series finished"