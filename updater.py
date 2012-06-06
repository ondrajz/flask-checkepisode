import os
import urllib
from config import MIRROR, REMOVE_OLD_IMAGES, IMAGE_FOLDER, PRINT_DETAIL
from checkepisode.models import *


def printDetail(msg):
    if PRINT_DETAIL:
        print msg


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
        printDetail("- - - - - - - - - - - - - - - - - - -")
        print "Updating series %s[%s]" % (series.name, series.tvdb_id)
        # -----------------------
        name = xmlSeries.findtext("SeriesName")
        if name:
            printDetail("Name = %s" % name)
            series.name = name
        # = = =
        overview = xmlSeries.findtext("Overview")
        if overview:
            printDetail("Overview = %s..." % overview[0:25])
            series.overview = overview
        # = = =
        lang = xmlSeries.findtext("Language")
        if lang:
            printDetail("Language = %s" % lang)
            series.language = getLanguage_id(lang)
        # = = =
        first_air = xmlSeries.findtext("FirstAired")
        if first_air:
            printDetail("First aired = %s" % first_air)
            series.first_aired = first_air.replace('-', '')
        # = = =
        air_dow = xmlSeries.findtext("Airs_DayOfWeek")
        if air_dow:
            printDetail("Day of week = %s" % air_dow)
            series.airs_dow = air_dow[:2]
        # = = =
        air_time = xmlSeries.findtext("Airs_Time")
        if air_time:
            printDetail("Air time = %s" % air_time)
            series.airs_time = air_time.replace(' ', '')
        # = = =
        genre = xmlSeries.findtext("Genre")
        if genre:
            printDetail("Genres = %s" % genre)
            series.genre = getGenres(genre)
        # = = =
        imdb = xmlSeries.findtext("IMDB_ID")
        if imdb:
            printDetail("imdb = %s" % imdb)
            series.imdb_id = imdb
        # = = =
        network = xmlSeries.findtext("Network")
        if network:
            printDetail("Network = %s" % network)
            series.network = getNetwork_id(network)
        # = = =
        rating = xmlSeries.findtext("Rating")
        if rating:
            printDetail("Rating = %s" % rating)
            series.tvdb_rating = rating
        # = = =
        rateCount = xmlSeries.findtext("RatingCount")
        if rateCount:
            printDetail("Rate count = %s" % rateCount)
            series.tvdb_ratecount = rateCount
        # = = =
        runtime = xmlSeries.findtext("Runtime")
        if runtime:
            printDetail("Runtime = %s" % runtime)
            series.runtime = runtime
        # = = =
        status = xmlSeries.findtext("Status")
        if status:
            printDetail("Status = %s" % status)
            series.status = getStatus_id(status)
        # = = =
        last = xmlSeries.findtext("lastupdated")
        if last:
            printDetail("Last update = %s" % last)
            series.last_update = last
        # = = =
        banner = xmlSeries.findtext("banner")
        if banner:
            printDetail("Banner = %s" % banner)
            series.banner = banner
            image_file = "%s%s" % (IMAGE_FOLDER, banner)
            dir_path = os.path.dirname(image_file)
            if not os.path.exists(dir_path):
                print "Creating %s" % dir_path
                os.makedirs(dir_path)
            if os.path.isfile(image_file) and REMOVE_OLD_IMAGES:
                printDetail("Removing old banner")
                os.remove(image_file)
            if not os.path.isfile(image_file):
                printDetail("Downloading banner")
                urllib.urlretrieve('%sbanners/%s' \
                    % (MIRROR, banner), image_file)
        # = = =
        poster = xmlSeries.findtext("poster")
        if poster:
            printDetail("Poster = %s" % poster)
            series.poster = poster
            image_file = "%s%s" % (IMAGE_FOLDER, poster)
            dir_path = os.path.dirname(image_file)
            if not os.path.exists(dir_path):
                print "Creating %s" % dir_path
                os.makedirs(dir_path)
            if os.path.isfile(image_file) and REMOVE_OLD_IMAGES:
                printDetail("Removing old poster")
                os.remove(image_file)
            if not os.path.isfile(image_file):
                printDetail("Downloading poster")
                urllib.urlretrieve('%sbanners/%s' \
                    % (MIRROR, poster), image_file)
        # -----------------------
        printDetail("- - - - - - - - - - - - - - - - - - -")


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
        printDetail("- - - - - - - - - - - - - - - - - - -")
        printDetail("Checking episode id = %s, seriesid = %s" % (epID, serID))
        if epID and serID:
            episode = getEpisode(epID, serID)
            if episode:
                printDetail("Updating episode")
                # -----------------------
                epName = xmlEpisode.findtext("EpisodeName")
                if epName:
                    printDetail("Name = %s" % epName)
                    episode.name = epName
                # = = =
                air_time = xmlEpisode.findtext("FirstAired")
                if air_time:
                    printDetail("Airing time = %s" % air_time)
                    episode.air_time = air_time.replace('-', '')
                # = = =
                seas_num = xmlEpisode.findtext("SeasonNumber")
                if seas_num:
                    printDetail("Season number = %s" % seas_num)
                    episode.seas_num = seas_num
                # = = =
                epis_num = xmlEpisode.findtext("EpisodeNumber")
                if epis_num:
                    printDetail("Episode number = %s" % epis_num)
                    episode.epis_num = epis_num
                # = = =
                overview = xmlEpisode.findtext("Overview")
                if overview:
                    printDetail("Overview = %s..." % overview[0:25])
                    episode.overview = overview
                # = = =
                tvdb_rating = xmlEpisode.findtext("Rating")
                if tvdb_rating:
                    printDetail("Rating = %s" % tvdb_rating)
                    episode.tvdb_rating = tvdb_rating
                # = = =
                tvdb_ratecount = xmlEpisode.findtext("RatingCount")
                if tvdb_ratecount:
                    printDetail("Rate count = %s" % tvdb_ratecount)
                    episode.tvdb_ratecount = tvdb_ratecount
                # = = =
                last_update = xmlEpisode.findtext("lastupdated")
                if last_update:
                    printDetail("Last update = %s" % last_update)
                    episode.last_update = last_update
                # = = =
                graphic = xmlEpisode.findtext("filename")
                if graphic:
                    printDetail("Graphic = %s" % graphic)
                    episode.graphic = graphic
                    image_file = "%s%s" % (IMAGE_FOLDER, graphic)
                    dir_path = os.path.dirname(image_file)
                    if not os.path.exists(dir_path):
                        print "Creating %s" % dir_path
                        os.makedirs(dir_path)
                    if os.path.isfile(image_file) and REMOVE_OLD_IMAGES:
                        printDetail("Removing old graphic")
                        os.remove(image_file)
                    if not os.path.isfile(image_file):
                        printDetail("Downloading graphic")
                        urllib.urlretrieve('%sbanners/%s' \
                            % (MIRROR, graphic), image_file)
                # -----------------------
            else:
                printDetail("Episode's series not in database")
        # -----------------------
        printDetail("- - - - - - - - - - - - - - - - - - -")
