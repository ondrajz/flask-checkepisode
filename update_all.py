import urllib
import zipfile
import os
from xml.etree import ElementTree as et
from datetime import datetime
from updater import *
from checkepisode.models import *
from config import API_KEY, MIRROR, REMOVE_OLD


def getInfoFile(ser_id):
    d = '%s/seriesZip' % os.getcwd()
    if not os.path.exists(d):
        print "Creating %s" % d
        os.makedirs(d)
    if ser_id:
        printDetail("Checking zipfile for %s" % ser_id)
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
            urllib.urlretrieve('%sapi/%s/series/%d/all/en.zip' \
                % (MIRROR, API_KEY, ser_id), tvdbZip)
            if os.path.isfile(tvdbZip):
                print "Extracting files from %s" % tvdbZip
                z = zipfile.ZipFile(tvdbZip, 'r')
                z.extractall(folder)
        else:
            printDetail("Found en.xml")
        return info


def getAllInfo(series):
    if series:
        printDetail("Retrieving all info about %s [%d]" \
            % (series.name, series.tvdb_id))
        info = getInfoFile(series.tvdb_id)
        if os.path.isfile(info):
            printDetail("Parsing en.xml")
            tvxml = et.parse(info)
            xmlSeries = tvxml.find('Series')
            if xmlSeries is not None:
                updateSeries(series, xmlSeries)
            xmlEpisodes = tvxml.findall('Episode')
            print "Found %d episodes" % len(xmlEpisodes)
            printDetail("- - - - - - - - - - - - - - - - - - -")
            x = 1
            for xmlEpisode in xmlEpisodes:
                printDetail("\n%d/%d episode of %s[%s]" \
                    % (x, len(xmlEpisodes), series.name, series.tvdb_id))
                x = x + 1
                updateEpisode(xmlEpisode)
        printDetail("\nRetrieving info finished\n")

series = Serie.query.all()
print "Starting update_all - %s" % datetime.now().strftime('%H:%M %d-%m-%Y')
print "Checking %d series\n" % len(series)
for s in series:
    printDetail("Checking %s[%s]" % (s.name, s.tvdb_id))
    if not s.last_update:
        printDetail("------------------------------------------------")
        if s.tvdb_id:
            getAllInfo(s)
            print "Committing to database.."
            db.session.commit()
        else:
            print "Missing tvdb_id!"
        printDetail("------------------------------------------------\n")
print "\nChecking series finished"
