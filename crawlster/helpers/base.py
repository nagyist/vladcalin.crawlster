class BaseHelper(object):
    """Base class for helpers"""
    is_helper = True

    def __init__(self):
        self.config = None
        self.crawler = None

    def initialize(self):
        """Perform initial configuration

        Called right after self.config and self.crawler is populated.
        """
        pass

    def finalize(self):
        """Perform cleanup on crawl finish"""
        pass
