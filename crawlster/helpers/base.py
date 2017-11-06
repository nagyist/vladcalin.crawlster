class BaseHelper(object):
    """Base class for helpers"""
    is_helper = True

    def __init__(self):
        self.config = None

    def initialize(self):
        """Perform initial configuration

        Called right after self.config is populated.
        """
        pass
