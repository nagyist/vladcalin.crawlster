import re
import bs4
import requests


class HttpResponse(object):
    def __init__(self, raw_response: requests.Response):
        self.status_code = raw_response.status_code
        self.headers = raw_response.headers
        self.cookies = raw_response.cookies

        self.content_binary = raw_response.content
        self.content_text = raw_response.text
        self.parsed_content = bs4.BeautifulSoup(raw_response.text, 'html.parser')

    def regex_search(self, pattern, flags=0):
        apply_to = self._get_regex_target(pattern)
        return re.search(pattern, apply_to, flags)

    def regex_findall(self, pattern, flags=0):
        apply_to = self._get_regex_target(pattern)
        return re.findall(pattern, apply_to, flags)

    def regex_match(self, pattern, flags=0):
        apply_to = self._get_regex_target(pattern)
        return re.match(pattern, apply_to, flags)

    def css(self, selector):
        return self.parsed_content.select(selector)

    def _get_regex_target(self, pattern):
        if isinstance(pattern, str):
            apply_to = self.content_text
        elif isinstance(pattern, bytes):
            apply_to = self.content_binary
        else:
            raise TypeError("Invalid type for regex pattern")
        return apply_to


class HttpSession(object):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                 "(KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"

    def __init__(self, proxy_factory=None):
        self.session = requests.Session()
        self.proxy_factory = proxy_factory

    def make_request(self, url, method="get", **kwargs):
        headers = {
            "User-Agent": self.user_agent
        }
        for k, v in kwargs.pop("headers", {}).items():
            headers[k] = v

        # get callable
        method = getattr(self.session, method)

        # make actual request
        response = method(url, headers=headers, **kwargs)
        return HttpResponse(response)

    def get(self, url, **kwargs):
        return self.make_request(url, method="get", **kwargs)

    def post(self, url, data=None, **kwargs):
        return self.make_request(url, method="post", data=data, **kwargs)


if __name__ == '__main__':
    session = HttpSession()

    resp = session.get("http://www.info.uaic.ro")

    print(resp.status_code)
    print(resp.cookies)
    print(resp.headers)
    print(resp.parsed_content)
    print(resp.content)
