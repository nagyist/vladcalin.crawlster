import requests

from crawlster.helpers.base import BaseHelper


class RequestsHelper(BaseHelper):
    name = 'requests'

    def __init__(self):
        super(RequestsHelper, self).__init__()
        self.session = None

    def initialize(self):
        self.session = requests.session()
