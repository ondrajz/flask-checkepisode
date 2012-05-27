from xml.etree import ElementTree as et
import urllib
import os
from config import MIRROR

def searchFor(name, all = False):
    from checkepisode.models import Series
    print "Searching for %s" % name
    results = []
    filehandle = urllib.urlopen("%sapi/GetSeries.php?seriesname=%s" % (MIRROR, urllib.quote(name)))
    xml = filehandle.read()
    tvxml = et.fromstring(xml)
    found_series = tvxml.findall('Series')
    for series in found_series:
        sId = int(series.findtext('seriesid'))
        if all or (not all and Series.query.filter_by(tvdb_id=sId).count()==0):
            sName = series.findtext('SeriesName')
            sFirstAired = series.findtext('FirstAired')
            sOverview = series.findtext('Overview')
            results.append({'name': sName, 'id': sId, 'first_aired': sFirstAired, 'overview': sOverview})
            print "%s [%d]" % (sName, sId)
    return results