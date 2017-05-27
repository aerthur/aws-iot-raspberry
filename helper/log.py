import logging
from logging.handlers import RotatingFileHandler

def configureLogs(appId, config):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(config['log']['path']+appId, 'a', 1000000, 1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    logger.addHandler(streamHandler)

