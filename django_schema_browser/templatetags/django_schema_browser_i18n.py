"""Template tags for bracketed translations."""

from django import template

from django_schema_browser.i18n import tr

register = template.Library()


@register.simple_tag
def btrans(message: str, **kwargs: object) -> str:
    return tr(message, **kwargs)
