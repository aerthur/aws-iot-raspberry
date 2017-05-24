import json
import pychromecast
import gmusicapi
from gmusicapi import Mobileclient
import time
import os

with open('config/config.json') as json_data_file:
    config = json.load(json_data_file)
print(config)

chromecasts = pychromecast.get_chromecasts()
cast = next(cc for cc in chromecasts if cc.device.friendly_name == "Music")
cast.wait()
print(cast.device)
mc = cast.media_controller

api = Mobileclient(False)
if api.login(config['google']['login'], config['google']['password'], api.FROM_MAC_ADDRESS, "fr_fr") != True:
    print("Unable to login")
else:
    print("*****************************************************************")
    songid=api.get_all_songs()[2]['id']
    print(songid)
    print("*****************************************************************")

    stream = api.get_stream_url(songid)
    mc.play_media(stream, 'audio/mp3')
    mc.block_until_active()
    mc.play()

    time.sleep(2)

    while mc.is_playing:
	    time.sleep(1)

    songid=api.get_all_songs()[1]['id']
    print(songid)
    stream = api.get_stream_url(songid)
    mc.play_media(stream, 'audio/mp3')
    mc.block_until_active()
    mc.play()
