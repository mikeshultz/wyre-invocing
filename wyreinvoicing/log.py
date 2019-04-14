import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


def get_logger(name):
    return log.getChild(name)
