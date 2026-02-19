"""Translation helpers for bracketed msgids."""

from django.utils.translation import gettext


def strip_brackets(value: str) -> str:
    text = str(value)
    if text.startswith("[") and text.endswith("]"):
        return text[1:-1]
    return text


def tr(message: str, **kwargs: object) -> str:
    translated = gettext(message)
    if kwargs:
        translated = translated % kwargs
    return strip_brackets(translated)
