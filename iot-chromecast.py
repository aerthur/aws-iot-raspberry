import json
import pychromecast
import gmusicapi
from gmusicapi import Mobileclient
import time
import os
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

with open('config/config.json') as json_data_file:
    config = json.load(json_data_file)
print(config)

allSongs=None
songIndex=25
shouldPlay=False

def playNextSong():
    global allSongs, songIndex,shouldPlay
    shouldPlay=False
    songIndex+=1
    if (songIndex>=len(allSongs)):
        songIndex = 0
    songid=allSongs[songIndex]['id']
    print("playing ",songIndex," ", songid, " ", len(allSongs))
    stream = api.get_stream_url(songid)
    mc.play_media(stream, 'audio/mp3')
    mc.block_until_active()
    mc.play()
    time.sleep(2)
    shouldPlay=True

def castCallback(client, userdata, message):
    print("Received a new message(button): ", message.payload, "from topic: ", message.topic)
    playNextSong()

# Init AWSIoTMQTTClient
aWSIoTMQTTClient = None
aWSIoTMQTTClient = AWSIoTMQTTClient("RASPBERRY-CHROMECAST")
aWSIoTMQTTClient.configureEndpoint(config['awsIot']['host'], config['awsIot']['port'])
aWSIoTMQTTClient.configureCredentials(config['awsIot']['rootCAPath'], config['awsIot']['privateKeyPath'], config['awsIot']['certificatePath'])
aWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
aWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
aWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
aWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
aWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
aWSIoTMQTTClient.connect()
aWSIoTMQTTClient.subscribe("/cast/music", 1, castCallback)

chromecasts = pychromecast.get_chromecasts()
cast = next(cc for cc in chromecasts if cc.device.friendly_name == "Music")
cast.wait()
print(cast.device)
mc = cast.media_controller
print("status ",mc.status)

api = Mobileclient(False)
if api.login(config['google']['login'], config['google']['password'], api.FROM_MAC_ADDRESS, "fr_fr") != True:
    print("Unable to login")
else:
    print("*****************************************************************")
    allSongs=api.get_all_songs()

    while True:
        time.sleep(0.1)
        if (shouldPlay and not mc.is_playing):
            playNextSong()
