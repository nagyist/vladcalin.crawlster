import os

from .validators import ValidationError, validate_isinstance, one_of
from .exceptions import ConfigurationError, OptionNotDefinedError, \
    MissingValueError


# Option specs


class ConfigOption(object):
    def __init__(self, validators, default=None, required=False):
        self.validators = validators
        self.default = default
        self.required = required

    def get_default_value(self):
        if callable(self.default):
            return self.default()
        else:
            return self.default


Optional = ConfigOption


class Required(ConfigOption):
    def __init__(self, validators):
        super(Required, self).__init__(validators, required=True)


class OptionWithDefaultValidators(ConfigOption):
    default_validators = []

    def __init__(self, default=None, required=False, extra_validators=None):
        validators = self.default_validators + (extra_validators or [])
        super(OptionWithDefaultValidators, self).__init__(validators,
                                                          default,
                                                          required)


class NumberOption(OptionWithDefaultValidators):
    default_validators = [validate_isinstance(int)]


class StringOption(OptionWithDefaultValidators):
    default_validators = [validate_isinstance(int)]


class ListOption(OptionWithDefaultValidators):
    default_validators = [validate_isinstance((list, tuple))]


class ChoiceOption(ConfigOption):
    def __init__(self, choices, default=None, required=False,
                 extra_validators=None):
        validators = [one_of(choices)] + (extra_validators or [])
        super(ChoiceOption, self).__init__(validators, default, required)


# Default values


DEFAULT_USER_AGENT = 'crawlster Python3'

# Options


CORE_OPTIONS = {
    'core.start_step': StringOption(required=True),
    'core.start_urls': ListOption(required=True),
    'core.workers': NumberOption(default=os.cpu_count())
}


# Core

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
        print(options_dict)
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
            raise Configuration(errors)

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
