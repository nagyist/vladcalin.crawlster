import sys
import logging
import logging.handlers

import colorlog

DEFAULT_LOG_FORMAT = ("%(log_color)s[%(asctime)s - %(name)s][%(levelname)s] "
                      "- %(funcName)s:%(lineno)s - %(message)s")


def get_logger(name):
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        colorlog.ColoredFormatter(
        ))
    console_handler.setLevel(logging.DEBUG)

    logger = logging.Logger(name)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)

    return logger
