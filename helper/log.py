import logging

def configureAwsIotLogs():
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

def configureLogs(appId, config):
    logging.basicConfig(filename=config['log']['path']+appId,level=logging.DEBUG)

