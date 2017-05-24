
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import paho.mqtt.client as mqtt
import sys
import logging
import time
import getopt

# Custom MQTT message callback
def lightCallback(client, userdata, message):
	print("Received a new message(light): ", message.payload, "from topic: ", message.topic)

def buttonCallback(client, userdata, message):
	print("Received a new message(button): ", message.payload, "from topic: ", message.topic)
	aWSIoTMQTTClient.publish(message.topic, message.payload, 1)

# Read in command-line parameters
host = ""
rootCAPath = ""
certificatePath = ""
privateKeyPath = ""
try:
	opts, args = getopt.getopt(sys.argv[1:], "hwe:k:c:r:", ["help", "endpoint=", "key=","cert=","rootCA="])
	if len(opts) == 0:
		raise getopt.GetoptError("No input parameters!")
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print(helpInfo)
			exit(0)
		if opt in ("-e", "--endpoint"):
			host = arg
		if opt in ("-r", "--rootCA"):
			rootCAPath = arg
		if opt in ("-c", "--cert"):
			certificatePath = arg
		if opt in ("-k", "--key"):
			privateKeyPath = arg
except getopt.GetoptError:
	print(usageInfo)
	exit(1)

# Missing configuration notification
missingConfiguration = False
if not host:
	print("Missing '-e' or '--endpoint'")
	missingConfiguration = True
if not rootCAPath:
	print("Missing '-r' or '--rootCA'")
	missingConfiguration = True
if not certificatePath:
	print("Missing '-c' or '--cert'")
	missingConfiguration = True
if not privateKeyPath:
	print("Missing '-k' or '--key'")
	missingConfiguration = True
if missingConfiguration:
	exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

#Init Pubsub
raspberryMQTTClient = mqtt.Client()
raspberryMQTTClient.on_message = buttonCallback
raspberryMQTTClient.connect("192.168.1.235", 1883, 60)
raspberryMQTTClient.subscribe("/#", 1)
raspberryMQTTClient.loop_start()

# Init AWSIoTMQTTClient
aWSIoTMQTTClient = None
aWSIoTMQTTClient = AWSIoTMQTTClient("RASPBERRY")
aWSIoTMQTTClient.configureEndpoint(host, 8883)
aWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
aWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
aWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
aWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
aWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
aWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
aWSIoTMQTTClient.connect()
aWSIoTMQTTClient.subscribe("ligh/hue", 1, lightCallback)
time.sleep(2)

# Publish to the same topic in a loop forever
while True:
	time.sleep(1)
