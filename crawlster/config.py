import os
from collections import namedtuple
import secrets

from .validators import ValidationError, validate_isinstance, one_of
from .exceptions import ConfigurationError, OptionNotDefinedError, \
    MissingValueError


# Option specs


class Option(object):
    def __init__(self, validators, default=None, required=False):
        self.validators = validators
        self.default = default
        self.required = required


class Required(Option):
    def __init__(self, validators):
        super(Required, self).__init__(validators, required=True)


# Default values


DEFAULT_USER_AGENT = 'crawlster Python3'


# Options


def merge_dicts(*dicts):
    res = {}
    for d in dicts:
        res.update(d)
    return res


HTTP_OPTIONS = {
    'http.user_agent': Option(validators=[validate_isinstance(str)],
                              default=DEFAULT_USER_AGENT),
}

CORE_OPTIONS = {
    'core.start_step': Required([validate_isinstance(str)]),
    'core.start_urls': Required([validate_isinstance(list)]),
}

URLS_OPTIONS = {
    'urls.allowed_domains': Option([validate_isinstance(list)],
                                   default=[]),
    'urls.forbidden_domains': Option([validate_isinstance(list)],
                                     default=[]),
}

POOL_OPTIONS = {
    'pool.workers': Option(validators=[validate_isinstance(int)],
                           default=os.cpu_count()),
}

LOG_OPTIONS = {
    'log.level': Option(
        [one_of('debug', 'info', 'warning', 'error', 'critical')],
        default='info'),
}



# Core

class Configuration(object):
    """Configuration object that stores key-value pairs of options"""

    defined_options = merge_dicts(HTTP_OPTIONS,
                                  CORE_OPTIONS,
                                  URLS_OPTIONS,
                                  POOL_OPTIONS,
                                  LOG_OPTIONS)

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
        for option_key in self.defined_options:
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
        if key not in self.options and option_spec.required:
            raise MissingValueError(
                '{} is required but not provided'.format(key))
        return self.options.get(key, option_spec.default)
