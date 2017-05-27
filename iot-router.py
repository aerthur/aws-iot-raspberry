import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
from helper.log import *
from helper.awsIot import *
import paho.mqtt.client as mqtt
import time
import getopt

app = "RASPBERRY-ROUTER"

with open('config/config.json') as json_data_file:
    config = json.load(json_data_file)
print(config)

def topicCallback(client, userdata, message):
    global aWSIoTMQTTClient
    logging.info("Receive from mosquitto")
    print("Received a new message(button): ", message.payload, "from topic: ", message.topic)
    aWSIoTMQTTClient.publish(message.topic, message.payload, 1)

def on_disconnect(client, userdata, rc):
    time.sleep(1)
    raspberryMQTTClient.reconnect()
    raspberryMQTTClient.loop_start

# Configure logging
configureLogs(app, config)

#Init Pubsub
raspberryMQTTClient = mqtt.Client()
raspberryMQTTClient.on_message = topicCallback
raspberryMQTTClient.connect(config['localIot']['host'], config['localIot']['port'], 60)
raspberryMQTTClient.subscribe("/#", 1)
raspberryMQTTClient.loop_start()
raspberryMQTTClient.on_disconnect = on_disconnect

# Init AWSIoTMQTTClient
aWSIoTMQTTClient = getAwsClient(app, config)
# Connect and subscribe to AWS IoT
aWSIoTMQTTClient.connect()

# Publish to the same topic in a loop forever
while True:
	time.sleep(0.1)
