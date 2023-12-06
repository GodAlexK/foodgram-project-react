from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from foodgram.constants import VALUE_ZERO


def validate_slug(slug: str):
    regex_validator = RegexValidator(
        regex=r'^[-a-zA-Z0-9_]+$',
        message='Только буквы и цифры')
    regex_validator(slug)


def validate_value_greater_zero(value):
    if value == VALUE_ZERO:
        raise ValidationError(
            f'Значение {value} не допускается',
            params={'value': value},)
