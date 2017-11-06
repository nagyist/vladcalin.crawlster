import importlib
from crawlster.util import get_logger
from crawlster.helpers import UrlsHelper, RegexHelper

DEFAULT_LOGGER = get_logger("default")


class Crawlster(object):
    HELPER_FLAG = 'is_helper'

    config = None

    # Helpers
    # we directly attach them because we want the nice auto complete
    # features of IDEs
    urls = UrlsHelper()
    regex = RegexHelper()

    def __init__(self):
        self.inject_config_into_helpers()

    def inject_config_into_helpers(self):
        for attrname in dir(self):
            attr_obj = getattr(self, attrname)
            if hasattr(attr_obj, self.HELPER_FLAG) and \
                    getattr(attr_obj, self.HELPER_FLAG):
                attr_obj.set_config(self.config)
