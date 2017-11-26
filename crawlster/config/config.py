import json
import os

from crawlster.config.options import StringOption, ListOption, NumberOption
from crawlster.validators import ValidationError
from crawlster.exceptions import ConfigurationError, OptionNotDefinedError, \
    MissingValueError

#: The core options used by the framework
CORE_OPTIONS = {
    'core.start_step': StringOption(required=True),
    'core.start_urls': ListOption(required=True),
    'core.workers': NumberOption(default=os.cpu_count())
}


class Configuration(object):
    """Configuration object that stores key-value pairs of options"""

    def __init__(self, options):
        """Initializes the values of the configuration object"""
        self.options = options
        self.defined_options = CORE_OPTIONS

    def register_options(self, options_dict):
        """Registers multiple option declarations in the current config """
        self.defined_options.update(options_dict)

    def __getattr__(self, item):
        return self.retrieve_value(item)

    def retrieve_value(self, key):
        """Retrieves a value. 

        If cannot determine its value, raises KeyError
        """
        return self.options[key]

    def get(self, key, **kwargs):
        """Retrieves the value of the specified option

        The returned value is the one passed in the config initialization or
        the default value.

        Args:
            key (str):
                The key of the option for which the value must be returned
            default:
                The default value to return if the specified key cannot
                be retrieved. If not specified, will raise a KeyError

        Raises:
            OptionNotDefinedError:
                When the specified key is not defined and raise_if_not_defined
                is True
        """
        try:
            value = self.retrieve_value(key)
            return value
        except KeyError:
            if 'default' not in kwargs:
                raise
            return kwargs.get('default')


class JsonConfiguration(Configuration):
    """Reads the configuration from a json file"""

    def __init__(self, file_path):
        with open(file_path, 'r') as fp:
            options = json.load(fp)
        super(JsonConfiguration, self).__init__(options)
