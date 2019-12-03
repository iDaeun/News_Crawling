import logging
import logging.handlers

def CreateLogger(logger_name, loggfile_path):
    logger = logging.getLogger(logger_name)
    if len(logger.handlers) > 0:
        return logger
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s|%(name)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
    # Create Handlers
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(formatter)

    fileHandler = logging.FileHandler(loggfile_path)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)

    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)

    return logger