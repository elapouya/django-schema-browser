"""Vues de navigation du schema Django."""

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from . import introspection


def home(request: HttpRequest) -> HttpResponse:
    context = {"apps": introspection.list_project_apps()}
    return render(request, "django_schema_browser/home.html", context)


def app_models(request: HttpRequest, app_label: str) -> HttpResponse:
    try:
        app_info = introspection.get_project_app(app_label)
        models = introspection.list_app_models(app_label)
    except LookupError as exc:
        raise Http404(str(exc)) from exc

    return render(
        request,
        "django_schema_browser/app_models.html",
        {"app": app_info, "models": models},
    )


def model_detail(request: HttpRequest, app_label: str, model_name: str) -> HttpResponse:
    try:
        details = introspection.get_model_details(app_label, model_name)
    except LookupError as exc:
        raise Http404(str(exc)) from exc
    return render(request, "django_schema_browser/model_detail.html", details)
