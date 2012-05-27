from xml.etree import ElementTree as et
import urllib
import os
from updater import *

def searchFor(name):
    print "Searching for %s" % name
    results = {}
    filehandle = urllib.urlopen("%sapi/GetSeries.php?seriesname=%s" % (MIRROR, urllib.quote(name)))
    xml = filehandle.read()
    tvxml = et.fromstring(xml)
    found_series = tvxml.findall('Series')
    if len(found_series)>0:
        for series in found_series:
            sName = series.findtext('SeriesName')
            sId = int(series.findtext('seriesid'))
            sFirstAired = series.findtext('FirstAired')
            sOverview = series.findtext('Overview')
            results[sName] = (sId, sFirstAired, sOverview)
            print "%s [%d]" % (sName, sId)
    return results