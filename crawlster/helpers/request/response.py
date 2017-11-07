from attr import attrs, attrib


@attrs
class HttpResponse(object):
    """Class representing a http response"""
    status_code = attrib()
    headers = attrib()
    content = attrib()
    request = attrib()
