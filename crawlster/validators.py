class ValidationError(Exception):
    """Thrown when validation fails"""


def validate_required(value):
    if not value:
        raise ValidationError('Is required')


def validate_isinstance(req_type):
    def actual_validator(value):
        if not isinstance(value, req_type):
            raise ValidationError(
                'Expected type {} byt got {} instead'.format(
                    req_type.__name__, type(value).__name__
                ))

    return actual_validator


def one_of(*choices):
    def actual_validator(value):
        if value not in choices:
            raise ValidationError(
                'Expected one of {} but got {} instead'.format(
                    ', '.join(choices), value
                ))

    return actual_validator
