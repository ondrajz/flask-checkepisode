from xml.etree import ElementTree as et
import urllib
import os
from config import MIRROR

def searchFor(name, all = False):
    from checkepisode.models import Series
    results = []
    filehandle = urllib.urlopen("%sapi/GetSeries.php?seriesname=%s" % (MIRROR, urllib.quote(name)))
    xml = filehandle.read()
    tvxml = et.fromstring(xml)
    found_series = tvxml.findall('Series')
    for series in found_series:
        id = int(series.findtext('seriesid'))
        if all or (not all and Series.query.filter_by(tvdb_id=id).count()==0):
            name = series.findtext('SeriesName')
            first_aired = series.findtext('FirstAired')
            overview = series.findtext('Overview')
            banner = series.findtext('banner')
            results.append({'name': name, 'tvdb_id': id, 'first_aired': first_aired, 'overview': overview, 'banner': banner})
    return results