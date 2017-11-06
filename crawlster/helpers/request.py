import requests
import requests.auth

from crawlster.helpers.base import BaseHelper


class RequestsHelper(BaseHelper):
    name = 'requests'

    def __init__(self):
        super(RequestsHelper, self).__init__()
        self.session = None
        self.auth = None

    def prepare_basic_auth(self, username, password):
        self.auth = requests.auth.HTTPBasicAuth(username, password)

    def initialize(self):
        self.session = requests.session()

    def make_request(self, *args, **kwargs):
        """Wrapper over request.request.

        See more:
            http://docs.python-requests.org/en/master/api/#requests.request
        """
        return self.session.request(*args, **kwargs)
