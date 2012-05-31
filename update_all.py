from checkepisode.models import *
from xml.etree import ElementTree as et
import urllib
import zipfile
import os
from updater import *
    
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
            x = 1
            for xmlEpisode in xmlEpisodes:
                print "- - - - - - - - - - - - - - - - - - -\nupdating %d/%d" % (x, len(xmlEpisodes))
                x = x + 1
                updateEpisode(xmlEpisode)
        print "\nRetrieving info finished\n"

series = Series.query.all()
print "Checking %d series\n" % len(series)
for s in series:
    print "Checking %s" % s.name
    if not s.last_update:
        print "------------------------------------------------"
        print "First update"
        if s.tvdb_id:
            getAllInfo(s)
            print "Committing to database.."
            db.session.commit()
        else:
            print "Missing ID!"
        print "------------------------------------------------\n"
print "Checking series finished"