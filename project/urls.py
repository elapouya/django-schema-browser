"""Configuration des URLs du projet."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("django_schema_browser.urls")),
]
