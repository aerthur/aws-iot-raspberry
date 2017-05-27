from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

def getAwsClient(deviceId, config):
    aWSIoTMQTTClient = None
    aWSIoTMQTTClient = AWSIoTMQTTClient(deviceId)
    aWSIoTMQTTClient.configureEndpoint(config['awsIot']['host'], config['awsIot']['port'])
    aWSIoTMQTTClient.configureCredentials(config['awsIot']['rootCAPath'], config['awsIot']['privateKeyPath'], config['awsIot']['certificatePath'])
    aWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    aWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    aWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    aWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    aWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    return aWSIoTMQTTClient
