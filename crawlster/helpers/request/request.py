from attr import attrs, attrib


@attrs
class HttpRequest(object):
    """Class representing a http request"""
    method = attrib(default='GET')
    url = attrib()
    params = attrib()
    data = attrib()
    headers = attrib()
    auth = attrib(default=None)
    cookies = attrib()
