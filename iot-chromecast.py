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

allLists = None
allSongs = None
currentList = ""
songIndex = -1
shouldPlay = False
mc = None
api = None

def manageNext(playList):
    global allSongs, songIndex,api,currentList
    try:
        allSongs = next(entry['tracks'] for entry in allLists if entry['name'] == playList)
        currentList=playList
    except:
        allSongs = allLists[0]['tracks']
    songIndex+=1
    if (songIndex>=len(allSongs)):
        songIndex = 0

def playNext(playList):
    global allSongs, songIndex,api
    manageNext(playList)
    songid = allSongs[songIndex]['trackId']
    print("playing ",songIndex," ", songid, " ", len(allSongs))
    stream = api.get_stream_url(songid)
    mc.play_media(stream, 'audio/mp3')
    mc.block_until_active()
    mc.play()
    time.sleep(2)

def playNextSong(playList, retry=True):
    global shouldPlay
    shouldPlay = False
    try:
        playNext(playList)
        shouldPlay=True
    except:
        print("retry...")
        if retry:
            tryConnectToCast()
            tryLogToGoogle()
            try:
                playNextSong(playList, False)
                shouldPlay=True
            except:
                None

def castCallback(client, userdata, message):
    print("Received a new message: ", message.payload, "from topic: ", message.topic)
    msg = json.loads(message.payload)
    if (msg['cmd']=="play"):
        playNextSong(msg['list'])

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
    global api,allSongs, allLists
    api = Mobileclient(False)
    if api.login(config['google']['login'], config['google']['password'], api.FROM_MAC_ADDRESS, "fr_fr") != True:
        return False
    print("*****************************************************************")
    #allSongs=api.get_all_songs()
    #allLists=api.get_all_playlists()
    allLists=api.get_all_user_playlist_contents()
    #print("*****************************************************************")
    #print("*****************************************************************")
    #print("*****************************************************************")
    #print(allSongs[0]) #7519279c-0afd-3b20-9295-715a09ae774b
    
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
        playNextSong(currentList)
