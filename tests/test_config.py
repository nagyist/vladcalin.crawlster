import pytest

from crawlster.config import Configuration, define, ConfigurationError, \
    OptionNotDefinedError
from crawlster.validators import validate_isinstance, validate_required, \
    ValidationError


def test_config_validate_single_option():
    old_defined = Configuration.defined_options
    Configuration.defined_options = {
        'test': define(validators=[validate_isinstance(int)], default=None)
    }
    config = Configuration({'test': 10})
    assert config.get('test') == 10

    with pytest.raises(ConfigurationError):
        Configuration({'test': 'not integer'})
    Configuration.defined_options = old_defined


def test_validators_required():
    validate_required(10)
    validate_required(True)
    validate_required('test')
    with pytest.raises(ValidationError):
        validate_required(None)
    with pytest.raises(ValidationError):
        validate_required(False)
    with pytest.raises(ValidationError):
        validate_required('')


def test_validators_is_instance():
    validate_isinstance(int)(10)
    validate_isinstance(str)('hello')
    validate_isinstance(bool)(True)
    validate_isinstance(list)(['hello', 'there'])
    with pytest.raises(ValidationError):
        validate_isinstance(int)('hello')
    with pytest.raises(ValidationError):
        validate_isinstance(str)(False)
    with pytest.raises(ValidationError):
        validate_isinstance(list)((1, 2, 3))


def test_config_accessing_wrong_option():
    old_defined = Configuration.defined_options
    Configuration.defined_options = {
        'test': define(validators=[validate_isinstance(int)], default=None)
    }
    config = Configuration({'test': 10})
    with pytest.raises(OptionNotDefinedError):
        config.get('hello')
    Configuration.defined_options = old_defined
