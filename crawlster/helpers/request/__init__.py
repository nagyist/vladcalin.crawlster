import requests
import requests.auth
import requests.exceptions

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
        """Initializes the session used for making requests"""
        self.session = requests.session()

    def make_request(self, *args, **kwargs):
        """Wrapper over request.request.

        See more:
            http://docs.python-requests.org/en/master/api/#requests.request
        """
        self.crawler.stats.incr(self.crawler.STAT_REQUESTS)
        try:
            resp = self.session.request(*args, **kwargs)
            self.crawler.stats.incr(self.crawler.STAT_DOWNLOAD,
                                    by=self._compute_resp_size(resp))
            self.crawler.stats.incr(self.crawler.STAT_UPLOAD,
                                    by=self._compute_req_size(resp.request))
            return resp
        except requests.exceptions.RequestException as e:
            self.crawler.log.error(str(e))

    def get(self, *args, **kwargs):
        """Makes a GET request"""
        return self.make_request('get', *args, **kwargs)

    def post(self, *args, **kwargs):
        """Makes a POST request"""
        return self.make_request('post', *args, **kwargs)

    def patch(self, *args, **kwargs):
        """Makes a PATCH request"""
        return self.make_request('patch', *args, **kwargs)

    def delete(self, *args, **kwargs):
        """Makes a DELETE request"""
        return self.make_request('delete', *args, **kwargs)

    def options(self, *args, **kwargs):
        """Makes an OPTIONS request"""
        return self.make_request('options', *args, **kwargs)

    def _compute_resp_size(self, response):
        return len(response.content)

    def _compute_req_size(self, request):
        return len(request.body or '')
