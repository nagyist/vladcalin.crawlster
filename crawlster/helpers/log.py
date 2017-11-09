import logging

import colorlog
import sys

from crawlster.config import ChoiceOption
from crawlster.helpers.base import BaseHelper


class LoggingHelper(BaseHelper):
    name = 'log'
    valid_log_levels = ('debug', 'info', 'warning', 'error', 'critical')
    config_options = {
        'log.level': ChoiceOption(valid_log_levels, default='info')
    }

    DEFAULT_FORMAT = "%(log_color)s%(levelname)s - %(name)s - %(message)s"

    def __init__(self):
        super(LoggingHelper, self).__init__()
        self.logger = None

    def initialize(self):
        level = self.parse_level(self.config.get('log.level'))

        logger = logging.getLogger('crawlster')
        stream_handler = self.make_stream_handler(level)
        logger.addHandler(stream_handler)
        logger.setLevel(level)
        self.logger = logger

    def make_stream_handler(self, level):
        colored_formatter = colorlog.ColoredFormatter(self.DEFAULT_FORMAT)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(colored_formatter)
        stream_handler.setLevel(level)
        return stream_handler

    def __getattr__(self, item):
        """Delegates method calls to the wrapped logger"""
        if item not in ('debug', 'info', 'warning', 'error', 'critical'):
            raise AttributeError()
        return getattr(self.logger, item)

    def parse_level(self, level_name):
        return getattr(logging, level_name.upper())
