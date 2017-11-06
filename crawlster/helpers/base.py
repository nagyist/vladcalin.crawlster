class BaseHelper(object):
    """Base class for helpers"""
    is_helper = True

    def __init__(self):
        self.config = None

    def set_config(self, configuration):
        """Injects the current configuration into the helpers"""
        self.config = configuration
