from collections import namedtuple

from .validators import ValidationError, validate_isinstance

# Option specs

OptionSpec = namedtuple('OptionSpec', 'validators default')


def define(validators, default):
    return OptionSpec(validators=validators, default=default)


# Default values


DEFAULT_USER_AGENT = 'crawlster Python3'


# Exceptions

class ConfigurationError(Exception):
    """Thrown when configuration is invalid"""


class OptionNotDefinedError(Exception):
    """Thrown when trying to access an option that is not defined"""


# Core

class Configuration(object):
    """Configuration object that stores key-value pairs of options"""

    defined_options = {
        'http.user_agent': define(validators=[validate_isinstance(str)],
                                  default=DEFAULT_USER_AGENT),
        'helpers.imports': define(
            validators=[validate_isinstance(list)], default=[])
    }

    def __init__(self, options):
        """Initializes the values of the configuration object

        Args:
            options (dict):
                the values of the configuration object
        """
        self.options = options
        errors = self.validate_options()
        if errors:
            raise ConfigurationError(errors)

    def validate_options(self):
        """Validates the options.

        Returns a mapping of option name - list of errors
        """
        errors = {}
        for option_key in self.options:
            op_errors = self.validate_single_option(option_key)
            if op_errors:
                errors[option_key] = op_errors
        return errors

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

    def get(self, key):
        """Retrieves the value of the specified option

        The returned value is the one passed in the config initialization or
        the default value.

        Args:
            key (str):
                The key of the option for which the value must be returned

        Raises:
            OptionNotDefinedError:
                When the specified key is not defined.
        """
        option_spec = self.defined_options.get(key)
        if not option_spec:
            raise OptionNotDefinedError(key)
        return self.options.get(key, option_spec.default)
