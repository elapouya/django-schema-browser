# django-schema-browser

`django-schema-browser` adds a web interface to introspect Django apps, their models, fields, and reverse relations.

## Installation

```bash
pip install django-schema-browser
```

## Configuration

In `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "django_schema_browser",
]
```

In the project's `urls.py`:

```python
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

urlpatterns += i18n_patterns(
    path("schema/", include("django_schema_browser.urls")),
)
```
