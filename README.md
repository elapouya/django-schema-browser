# django-schema-browser

Application Django qui introspecte les apps locales du projet et expose une navigation web:

- liste des applications detectees
- liste des modeles d'une application
- detail d'un modele (champs + relations inverses)

## Lancer le projet

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Puis ouvrir `http://127.0.0.1:8000/`.
