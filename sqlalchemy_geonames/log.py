import logging
import os
import sys


loggers = []


def configure_logging(log_level_name='WARNING',
                      handler=logging.StreamHandler):
    log_level = getattr(logging, log_level_name)
    logger = logging.getLogger()
    log_handler = handler(sys.stdout)
    log_handler.setLevel(log_level)
    logger.addHandler(log_handler)
    loggers.append(logger)


def get_logger():
    try:
        return loggers[0]
    except IndexError:
        log_level = os.environ.get('SQLALCHEMY_GEONAMES_LOG_LEVEL', 'WARNING')
        configure_logging(log_level)
        return loggers[0]
