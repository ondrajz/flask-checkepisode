from flaskext.script import Manager
from checkepisode import app, db
from checkepisode.series import Serie, Language, Genre, Network, Status
from checkepisode.episode import Episode
from checkepisode.settings.external import API_KEY, MIRROR, LAST_UPDATE,\
    IMAGE_FOLDER, REMOVE_OLD, SERIES_ZIP, REMOVE_OLD_IMAGES
from xml.etree import ElementTree as et
from datetime import datetime
import logging
import zipfile
import urllib
import os

manager = Manager(app)
logging.basicConfig(level=logging.DEBUG, format='%(message)s')


def getInfoFile(ser_id):
    if not os.path.exists(SERIES_ZIP):
        logging.info("Creating %s", SERIES_ZIP)
        os.makedirs(SERIES_ZIP)
    if ser_id:
        logging.debug("Checking zipfile for %s" % ser_id)
        tvdbZip = "%s/%s.zip" % (SERIES_ZIP, ser_id)
        folder = "%s/%s" % (SERIES_ZIP, ser_id)
        info = "%s/en.xml" % folder
        if os.path.isfile(info) and REMOVE_OLD:
            logging.info("Removing old files")
            if os.path.isfile(tvdbZip):
                logging.info("Removing old zipfile from %s", tvdbZip)
                os.remove(tvdbZip)
            if os.path.exists(folder):
                logging.info("Removing contents from %s", folder)
                for the_file in os.listdir(folder):
                    file_path = os.path.join(folder, the_file)
                    logging.info("Removing %s", file_path)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception, e:
                        logging.warning(e)
            else:
                os.makedirs(folder)
        if not os.path.isfile(info):
            logging.info("Retrieving zipfile for %s", ser_id)
            urllib.urlretrieve('%sapi/%s/series/%d/all/en.zip' \
                % (MIRROR, API_KEY, ser_id), tvdbZip)
            if os.path.isfile(tvdbZip):
                logging.info("Extracting files from %s", tvdbZip)
                z = zipfile.ZipFile(tvdbZip, 'r')
                z.extractall(folder)
        else:
            logging.debug("Found en.xml")
        return info


def getAllInfo(series):
    if series:
        logging.debug("Retrieving all info about %s [%d]",
            series.name, series.tvdb_id)
        info = getInfoFile(series.tvdb_id)
        if os.path.isfile(info):
            logging.debug("Parsing en.xml")
            tvxml = et.parse(info)
            xmlSeries = tvxml.find('Series')
            if xmlSeries is not None:
                updateSeries(series, xmlSeries)
            xmlEpisodes = tvxml.findall('Episode')
            logging.info("Found %d episodes", len(xmlEpisodes))
            logging.debug("- - - - - - - - - - - - - - - - - - -")
            x = 1
            for xmlEpisode in xmlEpisodes:
                logging.debug("\n%d/%d episode of %s[%s]",
                    x, len(xmlEpisodes), series.name, series.tvdb_id)
                x = x + 1
                updateEpisode(xmlEpisode)
        logging.debug("\nRetrieving info finished\n")


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
        logging.debug("- - - - - - - - - - - - - - - - - - -")
        logging.debug("Updating series %s[%s]", series.name, series.tvdb_id)
        # -----------------------
        name = xmlSeries.findtext("SeriesName")
        if name:
            logging.debug("Name = %s", name)
            series.name = name
        # = = =
        overview = xmlSeries.findtext("Overview")
        if overview:
            logging.debug("Overview = %s...", overview[0:25])
            series.overview = overview
        # = = =
        lang = xmlSeries.findtext("Language")
        if lang:
            logging.debug("Language = %s", lang)
            series.language = getLanguage_id(lang)
        # = = =
        first_air = xmlSeries.findtext("FirstAired")
        if first_air:
            logging.debug("First aired = %s", first_air)
            series.first_aired = first_air.replace('-', '')
        # = = =
        air_dow = xmlSeries.findtext("Airs_DayOfWeek")
        if air_dow:
            logging.debug("Day of week = %s", air_dow)
            series.airs_dow = air_dow[:2]
        # = = =
        air_time = xmlSeries.findtext("Airs_Time")
        if air_time:
            logging.debug("Air time = %s", air_time)
            series.airs_time = air_time.replace(' ', '')
        # = = =
        genre = xmlSeries.findtext("Genre")
        if genre:
            logging.debug("Genres = %s", genre)
            series.genre = getGenres(genre)
        # = = =
        imdb = xmlSeries.findtext("IMDB_ID")
        if imdb:
            logging.debug("imdb = %s", imdb)
            series.imdb_id = imdb
        # = = =
        network = xmlSeries.findtext("Network")
        if network:
            logging.debug("Network = %s", network)
            series.network = getNetwork_id(network)
        # = = =
        rating = xmlSeries.findtext("Rating")
        if rating:
            logging.debug("Rating = %s", rating)
            series.tvdb_rating = rating
        # = = =
        rateCount = xmlSeries.findtext("RatingCount")
        if rateCount:
            logging.debug("Rate count = %s", rateCount)
            series.tvdb_ratecount = rateCount
        # = = =
        runtime = xmlSeries.findtext("Runtime")
        if runtime:
            logging.debug("Runtime = %s", runtime)
            series.runtime = runtime
        # = = =
        status = xmlSeries.findtext("Status")
        if status:
            logging.debug("Status = %s", status)
            series.status = getStatus_id(status)
        # = = =
        last = xmlSeries.findtext("lastupdated")
        if last:
            logging.debug("Last update = %s", last)
            series.last_update = last
        # = = =
        banner = xmlSeries.findtext("banner")
        if banner:
            logging.debug("Banner = %s", banner)
            series.banner = banner
            image_file = "%s%s" % (IMAGE_FOLDER, banner)
            dir_path = os.path.dirname(image_file)
            if not os.path.exists(dir_path):
                print "Creating %s" % dir_path
                os.makedirs(dir_path)
            if os.path.isfile(image_file) and REMOVE_OLD_IMAGES:
                logging.debug("Removing old banner")
                os.remove(image_file)
            if not os.path.isfile(image_file):
                logging.debug("Downloading banner")
                urllib.urlretrieve('%sbanners/%s' \
                    % (MIRROR, banner), image_file)
        # = = =
        poster = xmlSeries.findtext("poster")
        if poster:
            logging.debug("Poster = %s", poster)
            series.poster = poster
            image_file = "%s%s" % (IMAGE_FOLDER, poster)
            dir_path = os.path.dirname(image_file)
            if not os.path.exists(dir_path):
                print "Creating %s" % dir_path
                os.makedirs(dir_path)
            if os.path.isfile(image_file) and REMOVE_OLD_IMAGES:
                logging.debug("Removing old poster")
                os.remove(image_file)
            if not os.path.isfile(image_file):
                logging.debug("Downloading poster")
                urllib.urlretrieve('%sbanners/%s' \
                    % (MIRROR, poster), image_file)
        # -----------------------
        logging.debug("- - - - - - - - - - - - - - - - - - -")


def getEpisode(epID, serID):
    old = Episode.query.filter_by(tvdb_id=epID).first()
    if old:
        return old
    series = Serie.query.filter_by(tvdb_id=serID).first()
    if series:
        new = Episode(epID)
        new.serie = series
        db.session.add(new)
        db.session.commit()
        return new
    else:
        return None


def updateEpisode(xmlEpisode):
    if xmlEpisode is not None:
        epID = xmlEpisode.findtext("id")
        serID = xmlEpisode.findtext("seriesid")
        logging.debug("- - - - - - - - - - - - - - - - - - -")
        logging.debug("Checking episode id = %s, seriesid = %s", epID, serID)
        if epID and serID:
            episode = getEpisode(epID, serID)
            if episode:
                logging.debug("Updating episode")
                # -----------------------
                epName = xmlEpisode.findtext("EpisodeName")
                if epName:
                    logging.debug("Name = %s", epName)
                    episode.name = epName
                # = = =
                air_time = xmlEpisode.findtext("FirstAired")
                if air_time:
                    logging.debug("Airing time = %s", air_time)
                    episode.air_time = air_time.replace('-', '')
                # = = =
                seas_num = xmlEpisode.findtext("SeasonNumber")
                if seas_num:
                    logging.debug("Season number = %s", seas_num)
                    episode.seas_num = seas_num
                # = = =
                epis_num = xmlEpisode.findtext("EpisodeNumber")
                if epis_num:
                    logging.debug("Episode number = %s", epis_num)
                    episode.epis_num = epis_num
                # = = =
                overview = xmlEpisode.findtext("Overview")
                if overview:
                    logging.debug("Overview = %s...", overview[0:25])
                    episode.overview = overview
                # = = =
                tvdb_rating = xmlEpisode.findtext("Rating")
                if tvdb_rating:
                    logging.debug("Rating = %s", tvdb_rating)
                    episode.tvdb_rating = tvdb_rating
                # = = =
                tvdb_ratecount = xmlEpisode.findtext("RatingCount")
                if tvdb_ratecount:
                    logging.debug("Rate count = %s", tvdb_ratecount)
                    episode.tvdb_ratecount = tvdb_ratecount
                # = = =
                last_update = xmlEpisode.findtext("lastupdated")
                if last_update:
                    logging.debug("Last update = %s", last_update)
                    episode.last_update = last_update
                # = = =
                graphic = xmlEpisode.findtext("filename")
                if graphic:
                    logging.debug("Graphic = %s", graphic)
                    episode.graphic = graphic
                    image_file = "%s%s" % (IMAGE_FOLDER, graphic)
                    dir_path = os.path.dirname(image_file)
                    if not os.path.exists(dir_path):
                        print "Creating %s" % dir_path
                        os.makedirs(dir_path)
                    if os.path.isfile(image_file) and REMOVE_OLD_IMAGES:
                        logging.debug("Removing old graphic")
                        os.remove(image_file)
                    if not os.path.isfile(image_file):
                        logging.debug("Downloading graphic")
                        urllib.urlretrieve('%sbanners/%s' \
                            % (MIRROR, graphic), image_file)
                # -----------------------
            else:
                logging.debug("Episode's series not in database")
        # -----------------------
        logging.debug("- - - - - - - - - - - - - - - - - - -")


def getSeriesXml(serID):
    if serID:
        filehandle = urllib.urlopen('%sapi/%s/series/%s/en.xml' \
            % (MIRROR, API_KEY, serID))
        try:
            tvxml = et.fromstring(filehandle.read())
        except:
            logging.warning("Failed xml parsing of:\n%s", filehandle.read())
            return None
        return tvxml.find('Series')
    return None


def getEpisodeXml(epID):
    if epID:
        filehandle = urllib.urlopen('%sapi/%s/episodes/%s/en.xml' \
            % (MIRROR, API_KEY, epID))
        try:
            tvxml = et.fromstring(filehandle.read())
        except:
            logging.warning("Failed xml parsing of:\n%s", filehandle.read())
            return None
        return tvxml.find('Episode')
    return None


@manager.command
def full():
    series = Serie.query.all()
    logging.info("Starting update_all - %s",
        datetime.now().strftime('%H:%M %d-%m-%Y'))
    logging.info("Checking %d series\n", len(series))
    for s in series:
        logging.info("Checking %s[%s]", s.name, s.tvdb_id)
        if not s.last_update:
            logging.debug("------------------------------------------------")
            if s.tvdb_id:
                getAllInfo(s)
                logging.debug("Committing to database..")
                db.session.commit()
            else:
                logging.info("Missing tvdb_id!")
            logging.debug("------------------------------------------------\n")
    logging.info("\nChecking series finished")


@manager.command
def periodic():
    updFile = open(LAST_UPDATE, 'r')
    last_time = int(updFile.readline())
    updFile.close()

    logging.info("Starting update - %s\nlast update = %s%s",
        datetime.now().strftime('%H:%M %d-%m-%Y'), last_time,
    "\n------------------------------------------------")
    filehandle = urllib.urlopen('%sapi/Updates.php?type=all&time=%s' \
        % (MIRROR, last_time))
    tvxml = et.fromstring(filehandle.read())

    new_update = tvxml.findtext("Time")
    series_updates = tvxml.findall('Series')
    episode_updates = tvxml.findall('Episode')

    logging.info("%d series updates\n%d episode updates",
        len(series_updates), len(episode_updates))

    x = 1
    logging.info("%sUpdating series",
        "------------------------------------------------\n")
    for s in series_updates:
        logging.debug("%d/%d series id = %s",
            x, len(series_updates), s.text)
        series = Serie.query.filter_by(tvdb_id=s.text).first()
        if series:
            updateSeries(series, getSeriesXml(s.text))
        x = x + 1

    x = 1
    logging.info("%sUpdating episodes",
        "------------------------------------------------\n")
    for e in episode_updates:
        logging.debug("%d/%d episode id = %s",
            x, len(episode_updates), e.text)
        updateEpisode(getEpisodeXml(e.text))
        x = x + 1

    logging.info("\nUpdating finished\nupdate time = %s\n%s", new_update,
        "================================================\n")
    updFile = open(LAST_UPDATE, 'w+')
    updFile.write(new_update)
    updFile.close()


if __name__ == "__main__":
    manager.run()
