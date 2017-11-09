import requests
import requests.auth
import requests.exceptions

from crawlster.helpers.base import BaseHelper
from crawlster.helpers.request.request import HttpRequest


class RequestsHelper(BaseHelper):
    name = 'http'

    STAT_DOWNLOAD = 'http.download'
    STAT_UPLOAD = 'http.upload'
    STAT_REQUESTS = 'http.requests'
    STAT_HTTP_ERRORS = 'http.errors'

    def __init__(self):
        super(RequestsHelper, self).__init__()
        self.session = None

    def initialize(self):
        """Initializes the session used for making requests"""
        self.session = requests.session()

    def make_request(self, url, method='get', query_params=None, data=None,
                     headers=None):
        """Wrapper over request.Session.request

        See more:
            http://docs.python-requests.org/en/master/api/#requests.Session.request
        """
        self.crawler.stats.incr(self.STAT_REQUESTS)

        try:
            resp = self.session.request(method, url, query_params, data,
                                        headers)
            self.crawler.stats.incr(self.STAT_DOWNLOAD,
                                    by=self._compute_resp_size(resp))
            self.crawler.stats.incr(self.STAT_UPLOAD,
                                    by=self._compute_req_size(resp.request))
            return resp
        except requests.exceptions.RequestException as e:
            self.crawler.stats.add(self.STAT_HTTP_ERRORS, e)
            self.crawler.log.error(str(e))

    def get(self, *args, **kwargs):
        """Makes a GET request"""
        return self.make_request(*args, **kwargs, method='get')

    def post(self, *args, **kwargs):
        """Makes a POST request"""
        return self.make_request(*args, **kwargs, method='post')

    def patch(self, *args, **kwargs):
        """Makes a PATCH request"""
        return self.make_request(*args, **kwargs, method='patch')

    def delete(self, *args, **kwargs):
        """Makes a DELETE request"""
        return self.make_request(*args, **kwargs, method='delete')

    def options(self, *args, **kwargs):
        """Makes an OPTIONS request"""
        return self.make_request(*args, **kwargs, method='options')

    def _compute_resp_size(self, response):
        return len(response.content)

    def _compute_req_size(self, request):
        return len(request.body or '')
