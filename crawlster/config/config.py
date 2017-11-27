import json
import os

from crawlster.config.options import StringOption, ListOption, NumberOption
from crawlster.exceptions import OptionNotDefinedError, \
    MissingValueError

#: The core options used by the framework
CORE_OPTIONS = {
    'core.start_step': StringOption(required=True),
    'core.start_urls': ListOption(required=True),
    'core.workers': NumberOption(default=os.cpu_count())
}


class Configuration(object):
    """Configuration object that stores key-value pairs of options"""

    def __init__(self, options=None):
        self.defined_opts = CORE_OPTIONS
        self.values = options or {}

    def register_options(self, options):
        self.defined_opts.update(options)

    def get(self, key):
        if key not in self.defined_opts:
            raise OptionNotDefinedError(
                'Option "{}" is not defined'.format(key))
        opt_specs = self.defined_opts[key]
        if key not in self:
            if opt_specs.required:
                raise MissingValueError(
                    'Option {} is required but its value '
                    'could not be determined'.format(key))
            else:
                return opt_specs.get_default_value()
        value = self[key]
        opt_specs.validate(value)
        return value

    def __contains__(self, item):
        """Returns whether the value is explicitly provided by the config"""
        return item in self.values

    def __getitem__(self, item):
        """Retireves the value of the """
        return self.values[item]

    def validate_options(self):
        for key in self.defined_opts:
            self.get(key)


class JsonConfiguration(Configuration):
    """Reads the configuration from a json file"""

    def __init__(self, file_path):
        super(JsonConfiguration, self).__init__()
        with open(file_path, 'r') as fp:
            options = json.load(fp)
        self.values = options
