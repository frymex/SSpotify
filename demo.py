#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyrighting 2022

# Telegram: t.me/cazzqev
# Github: https://github.com/frymex

from client.api import Credits, Spotify

# if you already authed and have "credentials.json"
# use spotify = Spotify(Credits())

# else
spotify = Spotify(Credits(email='my_enail@mail.com', password='secret!password'))

# for getting track info use example
track_info = spotify.song_info('track_id')

# for download use this
spotify.download_track(track_id='track_id', # spotify track_id
                       path='downloading_path', # folder to downloading song
                       set_tags=True # if you need set meta-tags set True
                       )

