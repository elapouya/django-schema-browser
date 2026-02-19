from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoSchemaBrowserConfig(AppConfig):
    """Web UI to browse Django apps and models from the project."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_schema_browser"
    verbose_name = _("[Django Schema Browser]")
