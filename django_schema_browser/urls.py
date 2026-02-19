"""URL patterns for django_schema_browser."""

from django.urls import path

from . import views

app_name = "django_schema_browser"

urlpatterns = [
    path("", views.home, name="home"),
    path("apps/<slug:app_label>/", views.app_models, name="app_models"),
    path("apps/<slug:app_label>/models/<slug:model_name>/", views.model_detail, name="model_detail"),
]
