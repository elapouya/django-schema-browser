"""Schema browser views."""

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.views.generic import TemplateView

from . import introspection


class SchemaBrowserPermissionRequiredMixin(PermissionRequiredMixin):
    permission_required = "django_schema_browser.can_access_schema_browser"
    raise_exception = True


class HomeView(SchemaBrowserPermissionRequiredMixin, TemplateView):
    template_name = "django_schema_browser/home.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        context["apps"] = introspection.list_project_apps()
        return context


class AppModelsView(SchemaBrowserPermissionRequiredMixin, TemplateView):
    template_name = "django_schema_browser/app_models.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        app_label = str(kwargs["app_label"])
        try:
            app_info = introspection.get_project_app(app_label)
            models = introspection.list_app_models(app_label)
        except LookupError as exc:
            raise Http404(str(exc)) from exc

        context["app"] = app_info
        context["models"] = models
        return context


class ModelDetailView(SchemaBrowserPermissionRequiredMixin, TemplateView):
    template_name = "django_schema_browser/model_detail.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        app_label = str(kwargs["app_label"])
        model_name = str(kwargs["model_name"])
        try:
            details = introspection.get_model_details(app_label, model_name)
        except LookupError as exc:
            raise Http404(str(exc)) from exc
        context.update(details)
        return context
