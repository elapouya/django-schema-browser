# django-schema-browser

`django-schema-browser` ajoute une interface web pour introspecter les apps Django, leurs modeles, champs et relations inverses.

## Installation

```bash
pip install django-schema-browser
```

## Configuration

Dans `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "django_schema_browser",
]
```

Dans `urls.py` du projet:

```python
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("schema/", include("django_schema_browser.urls")),
)
```

## Vues disponibles

- Home: liste des apps detectees
- Detail app: liste des modeles de l'app
- Detail modele: champs + relations inverses

## Build package (PyPI)

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

Upload TestPyPI:

```bash
python -m twine upload --repository testpypi dist/*
```

Upload PyPI:

```bash
python -m twine upload dist/*
```
