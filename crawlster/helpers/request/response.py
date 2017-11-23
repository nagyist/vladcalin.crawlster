class HttpResponse(object):
    """Class representing a http response"""

    def __init__(self, request, status_code, headers, body):
        """Initializes the http response object
        
        Args:
            request (HttpRequest):
                The request that produces this response
            status_code (int): 
                The status code as a number
            headers (dict):
                The response headers
            body:
                The body of the response, if any
        """
        self.request = request
        self.status_code = status_code
        self.headers = headers
        self.body = body
