import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import paho.mqtt.client as mqtt
import time
import getopt
import logging

with open('config/config.json') as json_data_file:
    config = json.load(json_data_file)
print(config)

def topicCallback(client, userdata, message):
	print("Received a new message(button): ", message.payload, "from topic: ", message.topic)
	aWSIoTMQTTClient.publish(message.topic, message.payload, 1)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

#Init Pubsub
raspberryMQTTClient = mqtt.Client()
raspberryMQTTClient.on_message = topicCallback
raspberryMQTTClient.connect(config['localIot']['host'], config['localIot']['port'], 60)
raspberryMQTTClient.subscribe("/#", 1)
raspberryMQTTClient.loop_start()

# Init AWSIoTMQTTClient
aWSIoTMQTTClient = None
aWSIoTMQTTClient = AWSIoTMQTTClient("RASPBERRY-ROUTER")
aWSIoTMQTTClient.configureEndpoint(config['awsIot']['host'], config['awsIot']['port'])
aWSIoTMQTTClient.configureCredentials(config['awsIot']['rootCAPath'], config['awsIot']['privateKeyPath'], config['awsIot']['certificatePath'])
aWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
aWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
aWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
aWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
aWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
aWSIoTMQTTClient.connect()

# Publish to the same topic in a loop forever
while True:
	time.sleep(1)
