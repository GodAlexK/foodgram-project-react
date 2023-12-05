from django.core.validators import RegexValidator


def validate_slug(slug: str):
    regex_validator = RegexValidator(
        regex=r'^[-a-zA-Z0-9_]+$',
        message='Только буквы и цифры')
    regex_validator(slug)