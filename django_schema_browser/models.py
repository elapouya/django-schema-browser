"""Models used to declare app-level permissions."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class SchemaBrowserAccess(models.Model):
    """Unmanaged model used to attach permissions to this app."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("can_access_schema_browser", _("Can access Django Schema Browser")),
        )
        verbose_name = _("Schema browser access")
        verbose_name_plural = _("Schema browser access")
