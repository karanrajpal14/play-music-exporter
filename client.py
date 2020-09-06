import sys
import os
import time
import json
from datetime import datetime
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
LOGS_DIR = "./logs"
NOW = datetime.now()
DOWNLOADED_LOG_FILENAME = f"{LOGS_DIR}/downloaded_{NOW}.txt"
LIBRARY_LOG_FILENAME = f"{LOGS_DIR}/all_songs_{NOW}.json"
POST_DOWNLOAD_DELETE = True

mm = Mobileclient()

if not os.path.exists(mobile_creds):
    mm.perform_oauth(storage_filepath=mobile_creds)
    devices = json.dumps(mm.get_registered_devices(),
                         ensure_ascii=False,
                         indent=4)
    print(
        "Here are your registered devices.",
        "Input one of id's into the .env file DEVICE_ID field without the '0x' and re-run the script."
    )
    print(devices)
    sys.exit(1)

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
    keepcharacters = (' ','.','_')
    safe_file_name = "".join(c for c in file_name if c.isalnum() or c in keepcharacters).rstrip()
    relative_file_path = f"{folder_name}/{safe_file_name}"

    play_count = song.get("playCount") or 0
    disc_number = song.get("discNumber")

    if os.path.exists(relative_file_path):
        print(f"{safe_file_name} is already downloaded")
    else:
        try:
            r = requests.get(stream_url, allow_redirects=True)
            wait_time = randint(5, 60)
            print(f"Waiting for {wait_time}s to prevent throttling the API")
            time.sleep(wait_time)

            print(f"Downloading {safe_file_name}")
            os.makedirs(folder_name, exist_ok=True)
            open(relative_file_path, 'wb+').write(r.content)

            content_length = int(r.headers.get('content-length'))
            downloaded_bytes = os.path.getsize(relative_file_path)

            if content_length == downloaded_bytes:
                print(f"Successfully downloaded {safe_file_name}")
                print("Adding ID3 tags")
                saved_song = eyed3.load(relative_file_path)
                saved_song.initTag()
                saved_song.tag.artist = artist
                saved_song.tag.album = album
                saved_song.tag.album_artist = album_artist
                saved_song.tag.title = title
                saved_song.tag.track_num = track_number
                saved_song.tag.play_count = play_count
                saved_song.tag.disc_num = disc_number
                saved_song.tag.save()
                print(f"Added ID3 tags for {safe_file_name}")
            else:
                print(
                    f"Incorrect file size for {safe_file_name}. Should be {content_length} bytes but downloaded only {downloaded_bytes} bytes."
                )
                print("Please delete the file and try again.")
                sys.exit(1)
        except Exception as e:
            print(
                f"Error {e}. Unable to write to {relative_file_path}. Please check your file/directory permissions."
            )
    return


downloaded = []
downloaded_logfile = open(DOWNLOADED_LOG_FILENAME, 'w+')
all_songs = mm.get_all_songs()
current_song_count = 0
all_songs_count = len(all_songs)

if all_songs_count:
    print(
        f"Found {len(all_songs)} songs in your library. Saved a summary to {LIBRARY_LOG_FILENAME}."
    )
    with open(LIBRARY_LOG_FILENAME, 'w+', encoding='utf-8') as f:
        json.dump(all_songs, f, ensure_ascii=False, indent=4)
    print()

    for song in all_songs:
        current_song_count += 1
        print(f"Downloading track {current_song_count} of {all_songs_count}")
        song_id = song.get("id")
        stream_url = mm.get_stream_url(song_id, device_id=DEVICE_ID)

        if is_downloadable(stream_url):
            download_song(stream_url)
            downloaded.append(song_id)
            if POST_DOWNLOAD_DELETE:
                mm.delete_songs(song_id)
                downloaded_logfile.write('%s\n' % song_id)
        else:
            print(f"Unable to download song {song.get('title')}")
        print()

    print(f"Successfully downloaded {len(downloaded)} songs")
else:
    print("Empty library. Please add some music to your library and re-run this script.")

print("Done!")