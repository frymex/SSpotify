#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyrighting 2022

# Telegram: t.me/cazzqev
# Github: https://github.com/frymex

import os
import json

from typing import Union

import music_tag
from librespot.core import Session
from librespot.metadata import TrackId
from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality

import requests
from pydub import AudioSegment


class _Config:
    _SESSION_PATH = './client/'

    SKIP_EXISTING_FILES = True
    MUSIC_FORMAT = os.getenv('MUSIC_FORMAT') or "mp3"  # "mp3" | "ogg"
    FORCE_PREMIUM = False  # set to True if not detecting your premium account automatically
    RAW_AUDIO_AS_IS = False or os.getenv(
        'RAW_AUDIO_AS_IS') == "y"  # set to True if you wish you save the raw audio without re-encoding it.
    # This is how many seconds ZSpotify waits between downloading tracks so spotify doesn't get out the ban hammer
    ANTI_BAN_WAIT_TIME = 5
    ANTI_BAN_WAIT_TIME_ALBUMS = 30
    # Set this to True to not wait at all between tracks and just go balls to the wall
    OVERRIDE_AUTO_WAIT = False
    CHUNK_SIZE = 50000

    LIMIT = 50

    requests.adapters.DEFAULT_RETRIES = 10
    REINTENT_DOWNLOAD = 30


# Methods
def sanitize_data(value):
    """ Returns given string with problematic removed """
    sanitize = ["\\", "/", ":", "*", "?", "'", "<", ">", '"']
    for i in sanitize:
        value = value.replace(i, "")
    return value.replace("|", "-")


def conv_artist_format(artists):
    """ Returns converted artist format """
    formatted = ""
    for artist in artists:
        formatted += artist + ", "
    return formatted[:-2]


def set_audio_tags(filename, artists, name, album_name, release_year, disc_number, track_number, track_id_str):
    """ sets music_tag metadata """
    tags = music_tag.load_file(filename)
    tags['artist'] = conv_artist_format(artists)
    tags['tracktitle'] = name
    tags['album'] = album_name
    tags['year'] = release_year
    tags['discnumber'] = disc_number
    tags['tracknumber'] = track_number
    tags['comment'] = 'id[spotify.com:track:' + track_id_str + ']'
    tags.save()

def set_music_thumbnail(filename, image_url):
    """ Downloads cover artwork """
    img = requests.get(image_url).content
    tags = music_tag.load_file(filename)
    tags['artwork'] = img
    tags.save()


# System
class Credits:
    def __init__(self,
                 email: Union[str] = None,
                 password: Union[str] = None):

        if os.path.isfile("credentials.json"):
            try:
                self.session = Session.Builder().stored_file().create()
            except RuntimeError:
                pass

        if self.session is None or not self.session.is_valid():
            self.session = Session.Builder().user_pass(email, password).create()

        if not self.session.is_valid():
            return


class Spotify:
    def __init__(self, credits: Credits):
        self.session: Session = credits.session
        self.premium = bool((self.session.get_user_attribute("type") == "premium") or False)
        self.credits = credits

        if self.premium:
            self.quality = AudioQuality.VERY_HIGH
        else:
            self.quality = AudioQuality.HIGH

    def _token(self):
        return self.session.tokens().get("user-read-email")

    def _convert_audio_format(self, filename: str):
        """ Converts raw audio into playable mp3 or ogg vorbis """
        raw_audio = AudioSegment.from_file(filename, format="ogg",
                                           frame_rate=44100, channels=2, sample_width=2)
        if self.quality == AudioQuality.VERY_HIGH:
            bitrate = "320k"
        else:
            bitrate = "160k"
        raw_audio.export(filename, format='mp3', bitrate=bitrate)

    def song_info(self, song_id: str):
        info = json.loads(requests.get("https://api.spotify.com/v1/tracks?ids=" + song_id +
                                       '&market=from_token',
                                       headers={"Authorization": "Bearer %s" % self._token()}).text)

        artists = []
        for data in info['tracks'][0]['artists']:
            artists.append(sanitize_data(data['name']))
        album_name = sanitize_data(info['tracks'][0]['album']["name"])
        name = sanitize_data(info['tracks'][0]['name'])
        image_url = info['tracks'][0]['album']['images'][0]['url']
        release_year = info['tracks'][0]['album']['release_date'].split("-")[0]
        disc_number = info['tracks'][0]['disc_number']
        track_number = info['tracks'][0]['track_number']
        scraped_song_id = info['tracks'][0]['id']
        is_playable = info['tracks'][0]['is_playable']

        return {
            'artists': artists,
            'album_name': album_name,
            'name': name,
            'image_url': image_url,
            'release_year': release_year,
            'disc_number': disc_number,
            'track_number': track_number,
            'scraped_song_id': scraped_song_id,
            'is_playable': is_playable
        }

    def download_track(self, track_id: str, path: str = './', set_tags: bool = False, extra_paths: str = '',
                       prefix: bool = False, prefix_value: str = ''):

        track_info = self.song_info(track_id)
        _artist = track_info['artists'][0]

        if prefix:
            _track_number = str(track_info['track_number']).zfill(2)
            song_name = f'{_artist} - {track_info["album_name"]} - {_track_number}. {track_info["name"]}.mp3'
            filename = os.path.join(path, extra_paths, song_name)
        else:
            song_name = f'{_artist} - {track_info["album_name"]} - {track_info["name"]}.mp3'
            filename = os.path.join(path, extra_paths, song_name)

        if not track_info['is_playable']:
            return

        if os.path.isfile(filename) and os.path.getsize(filename) and _Config.SKIP_EXISTING_FILES:
            return

        if track_id != track_info['scraped_song_id']:
            track_id_str = track_info['scraped_song_id']
        else:
            track_id_str = track_id

        track_id = TrackId.from_base62(track_id_str)

        stream = self.session.content_feeder().load(
            track_id, VorbisOnlyAudioQuality(self.quality), False, None)
        os.makedirs(path + extra_paths, exist_ok=True)

        total_size = stream.input_stream.size
        downloaded = 0
        fail = 0

        _CHUNK_SIZE = _Config.CHUNK_SIZE
        with open(filename, 'wb') as file:
            while downloaded <= total_size:

                data = stream.input_stream.stream().read(_CHUNK_SIZE)

                downloaded += len(data)
                file.write(data)
                if (total_size - downloaded) < _CHUNK_SIZE:
                    _CHUNK_SIZE = total_size - downloaded
                if len(data) == 0:
                    fail += 1
                if fail > _Config.REINTENT_DOWNLOAD:
                    break

            if not _Config.RAW_AUDIO_AS_IS:
                # self._convert_audio_format(filename)
                if set_tags:
                    set_audio_tags(filename, track_info["artists"], track_info["name"], track_info["album_name"],
                                   track_info["release_year"], track_info["disc_number"], track_info["track_number"],
                                   track_id_str)
                    set_music_thumbnail(filename, track_info["image_url"])

                return {
                    'path': path,
                    'track_info': track_info
                }

    def _session(self) -> Session:
        return self.session

    def _config(self) -> dict:
        return self.__dict__

    def _credits(self) -> dict:
        return self.credits.__dict__

