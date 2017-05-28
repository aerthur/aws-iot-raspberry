import json
from helper.log import *
from helper.awsIot import *
import pychromecast
import gmusicapi
from gmusicapi import Mobileclient
import time
import os
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

app = "RASPBERRY-CHROMECAST"
chromecastName = "Music"

with open('config/config.json') as json_data_file:
    config = json.load(json_data_file)
print(config)

# Configure logging
configureLogs(app, config)

allSongs = None
songIndex = 35
shouldPlay = False
mc = None
api = None

def playNext():
    global allSongs, songIndex,api
    songIndex+=1
    if (songIndex>=len(allSongs)):
        songIndex = 0
    songid = allSongs[songIndex]['id']
    print("playing ",songIndex," ", songid, " ", len(allSongs))
    stream = api.get_stream_url(songid)
    mc.play_media(stream, 'audio/mp3')
    mc.block_until_active()
    mc.play()
    time.sleep(2)

def playNextSong(retry=True):
    global shouldPlay
    shouldPlay = False
    try:
        playNext()
        shouldPlay=True
    except:
        print("retry...")
        if retry:
            tryConnectToCast()
            tryLogToGoogle()
            try:
                playNextSong(False)
                shouldPlay=True
            except:
                None

def castCallback(client, userdata, message):
    print("Received a new message: ", message.payload, "from topic: ", message.topic)
    msg = json.loads(message.payload)
    if (msg['cmd']=="play"):
        playNextSong()

def tryConnectToCast():
    global mc,chromecastName
    chromecasts = pychromecast.get_chromecasts()
    try:
        cast = next(cc for cc in chromecasts if cc.device.friendly_name == chromecastName)
    except:
        return False
    cast.wait()
    cast.quit_app()
    cast.wait()
    print(cast.device)
    mc = cast.media_controller
    print("*****************************************************************")
    print("status ",mc.status)
    print("*****************************************************************")
    return True

def tryLogToGoogle():
    global api,allSongs
    api = Mobileclient(False)
    if api.login(config['google']['login'], config['google']['password'], api.FROM_MAC_ADDRESS, "fr_fr") != True:
        return False
    print("*****************************************************************")
    allSongs=api.get_all_songs()
    return True

# Init Chromecast
tryConnectToCast()
#Init Google
tryLogToGoogle()

# Init AWSIoTMQTTClient
aWSIoTMQTTClient = getAwsClient(app, config)
aWSIoTMQTTClient.connect()
aWSIoTMQTTClient.subscribe("/cast/music", 1, castCallback)



while True:
    time.sleep(0.1)
    if (shouldPlay and not mc.is_playing):
        playNextSong()
