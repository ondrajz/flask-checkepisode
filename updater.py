from checkepisode.models import *
from xml.etree import ElementTree as et
from datetime import datetime
import os
import urllib

MIRROR = "http://www.thetvdb.com/"
API_KEY = "4E5D5C8EFC4175A1"
REMOVE_OLD = False
INSTANT_COMMIT = False
PRINT_COLUMN_DETAIL = INSTANT_COMMIT
REMOVE_OLD_IMAGES = False
IMAGE_FOLDER = "checkepisode/static/"

def getLanguage_id(lang):
    old = Language.query.filter_by(caption=lang).first()
    if old:
        return old
    new = Language(lang)
    db.session.add(new)
    return new
    
def getGenre_id(genre):
    old = Genre.query.filter_by(caption=genre).first()
    if old:
        return old
    new = Genre(genre)
    db.session.add(new)
    db.session.commit()
    return new
    
def getNetwork_id(network):
    old = Network.query.filter_by(caption=network).first()
    if old:
        return old
    new = Network(network)
    db.session.add(new)
    db.session.commit()
    return new
    
def getStatus_id(status):
    old = Status.query.filter_by(caption=status).first()
    if old:
        return old
    new = Status(status)
    db.session.add(new)
    db.session.commit()
    return new
    
def getGenres(genre):
    genres = []
    for gen in genre.split('|'):
        if gen:
            genres.append(getGenre_id(gen))
    return genres
    
def updateSeries(series, xmlSeries):
    if series and xmlSeries is not None:
        print "- - - - - - - - - - - - - - - - - - -"
        print "Updating series info, id = %s" % series.name
        # -----------------------
        overview = xmlSeries.findtext("Overview")
        if overview:
            if PRINT_COLUMN_DETAIL: print "Saving overview.."
            series.overview = overview
            if INSTANT_COMMIT: db.session.commit() 
        # = = =
        lang = xmlSeries.findtext("Language")
        if lang:
            if PRINT_COLUMN_DETAIL: print "Saving language.."
            series.language = getLanguage_id(lang)
            if INSTANT_COMMIT: db.session.commit() 
        # = = =
        first_air = xmlSeries.findtext("FirstAired")
        if first_air:
            if PRINT_COLUMN_DETAIL: print "Saving first aired.."
            series.first_aired = first_air.replace('-', '')
            #series.first_aired = datetime(first_air[0:4], first_air[4:2], first_air[6:2])
            if INSTANT_COMMIT: db.session.commit() 
        # = = =
        air_dow = xmlSeries.findtext("Airs_DayOfWeek")
        if air_dow:
            if PRINT_COLUMN_DETAIL: print "Saving airs day of week.."
            series.airs_dow = air_dow[:2]
            if INSTANT_COMMIT: db.session.commit() 
        # = = =
        air_time = xmlSeries.findtext("Airs_Time")
        if air_time:
            if PRINT_COLUMN_DETAIL: print "Saving air time.."
            series.airs_time = air_time.replace(' ', '')
            if INSTANT_COMMIT: db.session.commit() 
        # = = =
        genre = xmlSeries.findtext("Genre")
        if genre:
            if PRINT_COLUMN_DETAIL: print "Saving genres.."
            series.genre = getGenres(genre)
            if INSTANT_COMMIT: db.session.commit() 
        # = = =
        imdb = xmlSeries.findtext("IMDB_ID")
        if imdb:
            if PRINT_COLUMN_DETAIL: print "Saving imdb id.."
            series.imdb_id = imdb
            if INSTANT_COMMIT: db.session.commit() 
        # = = =
        network = xmlSeries.findtext("Network")
        if network:
            if PRINT_COLUMN_DETAIL: print "Saving network.."
            series.network = getNetwork_id(network)
            if INSTANT_COMMIT: db.session.commit() 
        # = = =
        rating = xmlSeries.findtext("Rating")
        if rating:
            if PRINT_COLUMN_DETAIL: print "Saving tvdb rating.."
            series.tvdb_rating = rating
            if INSTANT_COMMIT: db.session.commit() 
        # = = =
        rateCount = xmlSeries.findtext("RatingCount")
        if rateCount:
            if PRINT_COLUMN_DETAIL: print "Saving tvdb rate count.."
            series.tvdb_ratecount = rateCount
            if INSTANT_COMMIT: db.session.commit() 
        # = = =
        runtime = xmlSeries.findtext("Runtime")
        if runtime:
            if PRINT_COLUMN_DETAIL: print "Saving runtime.."
            series.runtime = runtime
            if INSTANT_COMMIT: db.session.commit() 
        # = = =
        status = xmlSeries.findtext("Status")
        if status:
            if PRINT_COLUMN_DETAIL: print "Saving status.."
            series.status = getStatus_id(status)
            if INSTANT_COMMIT: db.session.commit() 
        # = = =
        last = xmlSeries.findtext("lastupdated")
        if last:
            if PRINT_COLUMN_DETAIL: print "Saving last update.."
            series.last_update = last
            if INSTANT_COMMIT: db.session.commit() 
        # = = =
        banner = xmlSeries.findtext("banner")
        if banner:
            if PRINT_COLUMN_DETAIL: print "Saving banner.."
            series.banner = banner
            image_file = "%s%s" % (IMAGE_FOLDER, banner)
            dir_path = os.path.dirname(image_file)
            if not os.path.exists(dir_path):
                print "Creating %s" % dir_path
                os.makedirs(dir_path)
            if os.path.isfile(image_file) and REMOVE_OLD_IMAGES:
                if PRINT_COLUMN_DETAIL: print "Removing old banner"
                os.remove(image_file)
            if not os.path.isfile(image_file):
                if PRINT_COLUMN_DETAIL: print "Downloading banner"
                urllib.urlretrieve('%sbanners/%s' % (MIRROR, banner), image_file)
            if INSTANT_COMMIT: db.session.commit()
        # -----------------------
    
def getEpisode(epID, serID):
    old = Episode.query.filter_by(tvdb_id=epID).first()
    if old:
        return old
    series = Series.query.filter_by(tvdb_id=serID).first()
    if series:
        new = Episode(epID)
        new.series = series
        db.session.add(new)
        db.session.commit()
        return new
    else:
        return None
            
def updateEpisode(xmlEpisode):
    if xmlEpisode is not None:
        epID = xmlEpisode.findtext("id")
        serID = xmlEpisode.findtext("seriesid")
        print "- - - - - - - - - - - - - - - - - - -"
        print "Checking episode id = %s, seriesid = %s" % (epID, serID)
        if epID and serID:
            episode = getEpisode(epID, serID)
            if episode:
                print "Updating episode info"
                # -----------------------
                epName = xmlEpisode.findtext("EpisodeName")
                if epName:
                    if PRINT_COLUMN_DETAIL: print "Saving episode name.."
                    episode.name = epName
                    if INSTANT_COMMIT: db.session.commit() 
                # = = =
                air_time = xmlEpisode.findtext("FirstAired")
                if air_time:
                    if PRINT_COLUMN_DETAIL: print "Saving airing time.."
                    episode.air_time = air_time.replace('-', '')
                    #episode.air_time = datetime(air_time[0:4], air_time[4:2], air_time[6:2])
                    if INSTANT_COMMIT: db.session.commit() 
                # = = =
                seas_num = xmlEpisode.findtext("SeasonNumber")
                if seas_num:
                    if PRINT_COLUMN_DETAIL: print "Saving season number.."
                    episode.seas_num = seas_num
                    if INSTANT_COMMIT: db.session.commit() 
                # = = =
                epis_num = xmlEpisode.findtext("EpisodeNumber")
                if epis_num:
                    if PRINT_COLUMN_DETAIL: print "Saving episode number.."
                    episode.epis_num = epis_num
                    if INSTANT_COMMIT: db.session.commit() 
                # = = =
                overview = xmlEpisode.findtext("Overview")
                if overview:
                    if PRINT_COLUMN_DETAIL: print "Saving overview.."
                    episode.overview = overview
                    if INSTANT_COMMIT: db.session.commit() 
                # = = =
                tvdb_rating = xmlEpisode.findtext("Rating")
                if tvdb_rating:
                    if PRINT_COLUMN_DETAIL: print "Saving tvdb rating.."
                    episode.tvdb_rating = tvdb_rating
                    if INSTANT_COMMIT: db.session.commit() 
                # = = =
                tvdb_ratecount = xmlEpisode.findtext("RatingCount")
                if tvdb_ratecount:
                    if PRINT_COLUMN_DETAIL: print "Saving tvdb rate count.."
                    episode.tvdb_ratecount = tvdb_ratecount
                    if INSTANT_COMMIT: db.session.commit() 
                # = = =
                last_update = xmlEpisode.findtext("lastupdated")
                if last_update:
                    if PRINT_COLUMN_DETAIL: print "Saving last update.."
                    episode.last_update = last_update
                    if INSTANT_COMMIT: db.session.commit() 
                # = = =
                graphic = xmlEpisode.findtext("filename")
                if graphic:
                    if PRINT_COLUMN_DETAIL: print "Saving graphic.."
                    episode.graphic = graphic
                    image_file = "%s%s" % (IMAGE_FOLDER, graphic)
                    dir_path = os.path.dirname(image_file)
                    if not os.path.exists(dir_path):
                        print "Creating %s" % dir_path
                        os.makedirs(dir_path)
                    if os.path.isfile(image_file) and REMOVE_OLD_IMAGES:
                        if PRINT_COLUMN_DETAIL: print "Removing old graphic"
                        os.remove(image_file)
                    if not os.path.isfile(image_file):
                        if PRINT_COLUMN_DETAIL: print "Downloading graphic"
                        urllib.urlretrieve('%sbanners/%s' % (MIRROR, graphic), image_file)
                    if INSTANT_COMMIT: db.session.commit() 
                # -----------------------
            else:
                print "Episode's series not in database"