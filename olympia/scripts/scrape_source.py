import json
import os
import logging
from olympia import files, db
from olympia.data import song
from olympia.scraper import scrape_midis, process
from olympia import ROOT_DIR

logger = logging.getLogger("olympia")
logging.basicConfig(level=logging.DEBUG, format="%(message)s")


# METHOD: get_midi_id
# DESCRIPTION: get midi id from tracked midis
def get_midi_id(midi_url):
    query = """
    SELECT midi_id FROM midis
    WHERE url = :url
    """

    results = db.execute_query(query, {"url": midi_url})
    midi_id = results.first()[0]

    return midi_id


# METHOD: check_url_exists
# DESCRIPTION: check if a url exists in the midi table to avoid duplicates
def check_url_exists(midi_url):
    query = """
    SELECT count(*) FROM midis
    WHERE url = :url
    """

    results = db.execute_query(query, {"url": midi_url})
    count = results.first()[0]

    if count > 0:
        return True

    else:
        return False


# METHOD: process_midi
# DESCRIPTION: given a song item, add to s3 and db
def process_midi(song_item):

    # save song into midis table
    db.insert(
        "midis", {"url": song_item["url"], "song_title": song_item["title"], "artist": song_item["artist"],},
    )

    # get midi id and content
    midi_id = get_midi_id(song_item["url"])
    midi_content = scrape_midis.get_midi(song_item["url"])

    # write midi to local file
    local_file = f"{ROOT_DIR}/olympia/files/midis/raw_midi_{midi_id}.mid"
    with open(local_file, "wb") as f:
        f.write(midi_content)

    song_obj = song.Song(local_file)

    # update instruments in db
    query = """
    UPDATE midis SET instruments= :instruments, time_signature= :time_signature, expected_key= :expected_key WHERE midi_id= :midi_id
    """

    results = db.execute_query(
        query,
        {
            "instruments": json.dumps(song_obj.instruments),
            "time_signature": song_obj.time_signature,
            "expected_key": "_".join(str(song_obj.expected_key).lower().split(" ")),
            "midi_id": midi_id,
        },
    )

    save_file = f"midis/raw_midi_{midi_id}.mid"
    files.upload_file(local_file, save_file)

    # remove local file
    os.remove(local_file)

    logger.debug("Song, title: %s, artist: %s, processed!", song_item["title"], song_item["artist"])


# METHOD: scrape_midi_world
# DESCRIPTION: scrape midiworld to get download urls, then download and process midi files
def scrape_midiworld_midis():

    base_url = "https://www.midiworld.com/files/"
    for i in range(10000):

        midi_url = f"{base_url}{i}"

        # check if midi at path
        midi_content = scrape_midis.get_webpage(midi_url)

        if midi_content:

            # get songs
            songs = process.parse_midi_world_content(midi_content)

            # get each midi
            if songs:

                for i, song_item in enumerate(songs):

                    if not check_url_exists(song_item["url"]):

                        logger.debug("Processing song %s of %s", i, len(songs))

                        try:
                            process_midi(song_item)

                        except:
                            logger.debug("Failed to process %s", song_item["url"])


# METHOD: scrape_freemidi_midis
# DESCRIPTION: scrape freemidi
# TODO: CHECK THIS LOGIC
def scrape_freemidi_midis():

    values = "0abcdefghijklmnopqrstuvwxyz"
    base_url = "https://freemidi.org/artists-"

    for letter in values:
        midi_url = f"{base_url}{letter}"

        # check that the url hasn't already been scraped
        if not check_url_exists(midi_url):

            # check if midi at path
            midi_content = scrape_midis.get_webpage(midi_url)

            if midi_content:

                # get songs
                songs = process.parse_midi_world_content(midi_content)

                # get each midi
                if songs:

                    for song_item in songs:

                        process_midi(song_item)
