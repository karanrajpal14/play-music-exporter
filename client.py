import re
import sys
import os
import time
from random import randint

import requests
from dotenv import load_dotenv

from gmusicapi import Mobileclient
import eyed3

load_dotenv()

CREDS_DIR = "./creds"
DEVICE_ID = os.environ.get("DEV_ID")
mobile_creds = f"{CREDS_DIR}/mobileclient.cred"

MUSIC_DIR = "./music"

mm = Mobileclient()

if not os.path.exists(mobile_creds):
    mm.perform_oauth(storage_filepath=mobile_creds)

mm.oauth_login(oauth_credentials=mobile_creds, device_id=DEVICE_ID)

if not mm.is_authenticated():
    print("Not authenticated")
    sys.exit(1)


def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True


def download_song(stream_url):
    album = song.get("album")
    album_artist = song.get("albumArtist")
    folder_name = f"{MUSIC_DIR}/{album_artist}_{album}"

    title = song.get("title")
    artist = song.get("artist")
    track_number = song.get("trackNumber")
    year = song.get("year")
    file_name = f"{track_number:0>2}_{title}_{artist}_({year}).mp3"
    relative_file_path = f"{folder_name}/{file_name}"

    if os.path.exists(relative_file_path):
        print(f"{file_name} is already downloaded")
    else:
        try:
            r = requests.get(stream_url, allow_redirects=True)
            wait_time = randint(5, 60)
            print(f"Waiting for {wait_time}s to prevent throttling the API")
            time.sleep(wait_time)

            print(f"Downloading {file_name}")
            os.makedirs(folder_name, exist_ok=True)
            open(relative_file_path, 'wb+').write(r.content)

            content_length = int(r.headers.get('content-length'))
            downloaded_bytes = os.path.getsize(relative_file_path)

            if content_length == downloaded_bytes:
                print(f"Successfully downloaded {file_name}")
            else:
                print(
                    f"Incorrect file size for {file_name}. Should be {content_length} bytes but downloaded only {downloaded_bytes} bytes."
                )
                print("Please delete the file and try again.")
                sys.exit(1)
        except Exception as e:
            print(
                f"Error {e}. Unable to write to {relative_file_path}. Please check your file/directory permissions."
            )


all_songs = mm.get_all_songs()[:2]

for song in all_songs:
    song_id = song.get("id")
    stream_url = mm.get_stream_url(song_id, device_id=DEVICE_ID)

    if is_downloadable(stream_url):
        download_song(stream_url)
    else:
        print(f"Unable to download song {song.get('title')}")

# Save ID3 tags
# add song id to delete list
# invoke delete from library once done