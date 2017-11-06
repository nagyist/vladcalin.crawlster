import urllib.parse

from crawlster.helpers.base import BaseHelper


class UrlsHelper(BaseHelper):
    """Helper that provides shortcuts to various url operations"""
    name = 'urls'

    def __init__(self):
        super(UrlsHelper, self).__init__()

    def join(self, base, *parts):
        """Joins multiple url parts with the base.

        Note:
            if any part is an absolute url, it will overwrite the parts from
            before it.
        """
        res = base
        for part in parts:
            res = urllib.parse.urljoin(res, part)
        return res

    def join_paths(self, base, paths):
        return [self.join(base, path) for path in paths]

    def get_hostname(self, url):
        """Returns only the hostname of the url (domain and subdomains)."""
        return urllib.parse.urlparse(url).netloc

    def get_base(self, url):
        return self.join(url, '/')

    def get_path(self, url):
        """Returns the URL path for the url"""
        return urllib.parse.urlparse(url).path

    def urlencode(self, data):
        """Creates a query string from data"""
        return urllib.parse.urlencode(data)
