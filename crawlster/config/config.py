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
        """Initializes the values of the configuration object

        Args:
            options (dict):
                the values of the configuration object
        """
        self.provided_options = options
        self.defined_options = CORE_OPTIONS

    def register_options(self, options_dict):
        """Registers multiple option declarations in the current config """
        self.defined_options.update(options_dict)

    def validate_options(self):
        """Validates the options.

        Returns a mapping of option name - list of errors
        """
        errors = {}
        for option_key in self.defined_options:
            op_errors = self.validate_single_option(option_key)
            if op_errors:
                errors[option_key] = op_errors
        if errors:
            raise ConfigurationError(errors)

    def validate_single_option(self, option_name):
        """Validates a single option given its name

        Runs the validators for a single value.

        Raises:
            OptionNotDefinedError:
                when the option_name is not defined in the defined_options

        Returns:
            A list of error messages from the validators
        """
        errors = []
        option_spec = self.defined_options.get(option_name)
        option_value = self.get(option_name)
        for validator in option_spec.validators:
            try:
                validator(option_value)
            except ValidationError as e:
                errors.append(str(e))
        return errors

    def get(self, key, *, raise_if_not_defined=True):
        """Retrieves the value of the specified option

        The returned value is the one passed in the config initialization or
        the default value.

        Args:
            key (str):
                The key of the option for which the value must be returned
            raise_if_not_defined (bool):
                Whether to raise an exception if the required option is not
                defined. If False and the option is not defined, None is
                returned.

        Raises:
            OptionNotDefinedError:
                When the specified key is not defined and raise_if_not_defined
                is True
        """
        option_spec = self.defined_options.get(key)
        if not option_spec:
            if raise_if_not_defined:
                raise OptionNotDefinedError(key)
            else:
                return
        if key not in self.provided_options and option_spec.required:
            raise MissingValueError(
                '{} is required but not provided'.format(key))
        return self.provided_options.get(key, option_spec.get_default_value())


class JsonConfiguration(Configuration):
    """Reads the configuration from a json file"""

    def __init__(self, file_path):
        with open(file_path, 'r') as fp:
            options = json.load(fp)
        super(JsonConfiguration, self).__init__(options)
