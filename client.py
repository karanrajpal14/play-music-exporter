from gmusicapi import Mobileclient, Musicmanager
from pprint import pprint
from dotenv import load_dotenv
import requests
import re
import sys
import os
import eyed3

load_dotenv()

CREDS_DIR="./creds"
DEVICE_ID=os.environ.get("DEV_ID")
mobile_creds=f"{CREDS_DIR}/mobileclient.cred"
man_creds=f"{CREDS_DIR}/mma.cred"

MUSIC_DIR="./music"

mm = Mobileclient()
mma = Musicmanager()

if not os.path.exists(mobile_creds):
    mm.perform_oauth(storage_filepath=mobile_creds)

if not os.path.exists(man_creds):
    mma.perform_oauth(storage_filepath=man_creds)

mm.oauth_login(oauth_credentials=mobile_creds, device_id=DEVICE_ID)
mma.login(oauth_credentials=man_creds)

if not mm.is_authenticated():
    print("Not authenticated")
    sys.exit()


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


def download_song(song_id, file_name):
    stream_url = mm.get_stream_url(song_id, device_id=DEVICE_ID)
    downloadable = is_downloadable(stream_url)
    if downloadable:
        r = requests.get(stream_url, allow_redirects=True)
        download_url = r.url
        content_type = r.headers.get('content-type')
        content_length = int(r.headers.get('content-length'))
        try:
            open(file_name, 'wb+').write(r.content)
            downloaded_bytes = os.path.getsize(file_name)
            if content_length == downloaded_bytes:
                print(f"Successfully downloaded {file_name}")
            else:
                print(f"Incorrect file size for {file_name}. Should be {content_length} bytes but downloaded only {downloaded_bytes} bytes.")
                print("Please delete the file and try again.")
                sys.exit(1)
        except:
            print(f"Unable to write {file_name}")
    else:
        print(f"Unable to download {file_name}!")
        print("Exiting")
        sys.exit(1)



all_songs = mm.get_all_songs()[:1]


for song in all_songs:
    song_id = song.get("id")
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
        print(f"Downloading {file_name}")
        os.makedirs(folder_name)
        download_song(song_id, relative_file_path)



#     # add song id to delete list
#     # invoke delete from library once done