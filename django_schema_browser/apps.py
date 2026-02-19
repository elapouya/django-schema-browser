from django.apps import AppConfig


class DjangoSchemaBrowserConfig(AppConfig):
    """Interface web pour explorer les applications et modeles Django du projet."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_schema_browser"
    verbose_name = "Django Schema Browser"
