import pytest

from crawlster.helpers.request.request import HttpRequest


def test_request_invalid_method():
    with pytest.raises(ValueError):
        HttpRequest(method='invalid', url="http://example.com")
