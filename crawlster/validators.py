"""This module contains various validators.

They are used mainly in the config options definitions.
"""
import urllib.parse


class ValidationError(Exception):
    """Thrown when validation fails"""


def validate_isinstance(req_type):
    """Validates that an instance is of a certain type"""

    def actual_validator(value):
        if not isinstance(value, req_type):
            raise ValidationError(
                'Expected type {} byt got {} instead'.format(
                    type(req_type).__name__, type(value).__name__
                ))

    return actual_validator


def one_of(*choices):
    """Validates that an instance is one of the specified values"""

    def actual_validator(value):
        if value not in choices:
            raise ValidationError(
                'Expected one of {} but got {} instead'.format(
                    ', '.join((str(c) for c in choices)), value
                ))

    return actual_validator


def is_url(value):
    """Validates that the value represents a valid URL"""
    result = urllib.parse.urlparse(value)
    if result.scheme and result.netloc:
        return True
    else:
        raise ValidationError('Invalid URL: {}'.format(value))
