from attr import attrs, attrib


@attrs
class HttpRequest(object):
    """Class representing a http request"""
    #: the url where to make the request
    url = attrib()
    #: the http verb
    method = attrib(default='GET')
    #: http query strings
    query_params = attrib(default=None)
    #: Body for POST/PATCH requests
    data = attrib(default=None)
    #: mapping of headers
    headers = attrib(default=None)
