"""URL patterns for django_schema_browser."""

from django.urls import path

from . import views

app_name = "django_schema_browser"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("apps/<slug:app_label>/", views.AppModelsView.as_view(), name="app_models"),
    path("apps/<slug:app_label>/models/<slug:model_name>/", views.ModelDetailView.as_view(), name="model_detail"),
]
