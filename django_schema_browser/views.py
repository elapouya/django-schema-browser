"""Schema browser views."""

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import activate

from . import introspection


def _activate_language_from_url(request: HttpRequest) -> None:
    first_segment = request.path_info.lstrip("/").split("/", 1)[0]
    available_languages = {code for code, _label in settings.LANGUAGES}
    if first_segment in available_languages:
        activate(first_segment)


def home(request: HttpRequest) -> HttpResponse:
    _activate_language_from_url(request)
    context = {"apps": introspection.list_project_apps()}
    return render(request, "django_schema_browser/home.html", context)


def app_models(request: HttpRequest, app_label: str) -> HttpResponse:
    _activate_language_from_url(request)
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
    _activate_language_from_url(request)
    try:
        details = introspection.get_model_details(app_label, model_name)
    except LookupError as exc:
        raise Http404(str(exc)) from exc
    return render(request, "django_schema_browser/model_detail.html", details)
