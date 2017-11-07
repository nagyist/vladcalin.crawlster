import sys
import pprint

from .base import BaseItemHandler


class LogItemHandler(BaseItemHandler):
    def __init__(self):
        super(LogItemHandler, self).__init__()
        self.logger = None

    def handle(self, item):
        self.crawler.log.warning(pprint.pformat(item, indent=4) + '\n')
