"""Introspection services for Django apps and models."""

from __future__ import annotations

import ast
import importlib
import inspect
import textwrap
from pathlib import Path
from typing import Any

from django.apps import AppConfig, apps
from django.conf import settings
from django.db.models import Model

from .i18n import strip_brackets, tr

NO_DESCRIPTION = "[No description.]"


def _normalize_text(text: Any) -> str:
    if not text:
        return ""
    cleaned = " ".join(str(text).split())
    return cleaned.strip()


def _pick_description(*candidates: Any) -> str:
    for candidate in candidates:
        normalized = _normalize_text(candidate)
        if normalized:
            return normalized
    return tr(NO_DESCRIPTION)


def _is_project_path(path: str) -> bool:
    project_root = Path(settings.BASE_DIR).resolve()
    resolved = Path(path).resolve()
    try:
        resolved.relative_to(project_root)
        return True
    except ValueError:
        return False


def _project_app_configs() -> list[AppConfig]:
    configs = [config for config in apps.get_app_configs() if _is_project_path(config.path)]
    return sorted(configs, key=lambda config: config.label)


def _module_docstring(module_name: str) -> str:
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        return ""
    return inspect.getdoc(module) or ""


def _file_module_docstring(file_path: Path) -> str:
    if not file_path.exists() or not file_path.is_file():
        return ""
    try:
        source = file_path.read_text(encoding="utf-8")
    except OSError:
        return ""
    try:
        module_ast = ast.parse(source)
    except SyntaxError:
        return ""
    return ast.get_docstring(module_ast) or ""


def _app_description(app_config: AppConfig) -> str:
    app_class_doc = ""
    if app_config.__class__.__module__.endswith(".apps"):
        # __doc__ avoids inherited docstring from django.apps.AppConfig.
        app_class_doc = app_config.__class__.__doc__ or ""
    package_module_doc = _module_docstring(app_config.name)
    apps_module_doc = _module_docstring(app_config.__class__.__module__)
    init_file_doc = _file_module_docstring(Path(app_config.path) / "__init__.py")
    verbose_name = strip_brackets(str(app_config.verbose_name))
    default_verbose_name = app_config.label.replace("_", " ")
    if verbose_name.lower() == default_verbose_name.lower():
        verbose_name = ""

    parts = [
        _normalize_text(verbose_name),
        _normalize_text(app_class_doc),
        _normalize_text(apps_module_doc),
        _normalize_text(init_file_doc),
        _normalize_text(package_module_doc),
    ]
    unique_parts = [part for part in dict.fromkeys(parts) if part]
    return " | ".join(unique_parts) if unique_parts else tr(NO_DESCRIPTION)


def _model_description(model: type[Model]) -> str:
    model_doc = inspect.getdoc(model)
    verbose_name = str(model._meta.verbose_name)
    default_verbose_name = model.__name__.replace("_", " ")
    if verbose_name.lower() == default_verbose_name.lower():
        verbose_name = ""
    return _pick_description(model_doc, verbose_name)


def _explicit_class_docstring(model: type[Model]) -> str:
    """Return only the class-level docstring explicitly declared on the class."""
    try:
        source = inspect.getsource(model)
    except (OSError, TypeError):
        return ""

    try:
        module_ast = ast.parse(textwrap.dedent(source))
    except SyntaxError:
        return ""

    for node in module_ast.body:
        if isinstance(node, ast.ClassDef) and node.name == model.__name__:
            return ast.get_docstring(node) or ""
    return ""


def _model_detail_description(model: type[Model]) -> str:
    return _pick_description(_explicit_class_docstring(model))


def _field_type(field: Any) -> str:
    if hasattr(field, "get_internal_type"):
        try:
            return field.get_internal_type()
        except (AttributeError, TypeError):
            pass
    return field.__class__.__name__


def _field_description(field: Any) -> str:
    verbose_name = getattr(field, "verbose_name", "")
    help_text = getattr(field, "help_text", "")
    field_name = getattr(field, "name", "")
    if _normalize_text(verbose_name).lower() == field_name.replace("_", " ").lower():
        verbose_name = ""
    return _pick_description(help_text, verbose_name)


def _find_project_app_config(app_label: str) -> AppConfig:
    for app_config in _project_app_configs():
        if app_config.label == app_label:
            return app_config
    raise LookupError(tr("[App not found: %(app_label)s]", app_label=app_label))


def list_project_apps() -> list[dict[str, Any]]:
    app_entries = []
    for app_config in _project_app_configs():
        models = list(app_config.get_models())
        description = _app_description(app_config)
        app_entries.append(
            {
                "label": app_config.label,
                "name": strip_brackets(str(app_config.verbose_name)),
                "module": app_config.name,
                "description": description,
                "has_description": description != tr(NO_DESCRIPTION),
                "models_count": len(models),
            }
        )
    return sorted(app_entries, key=lambda app_entry: app_entry["name"].lower())


def get_project_app(app_label: str) -> dict[str, Any]:
    app_config = _find_project_app_config(app_label)
    models = list(app_config.get_models())
    description = _app_description(app_config)
    return {
        "label": app_config.label,
        "name": strip_brackets(str(app_config.verbose_name)),
        "module": app_config.name,
        "description": description,
        "has_description": description != tr(NO_DESCRIPTION),
        "models_count": len(models),
    }


def list_app_models(app_label: str) -> list[dict[str, Any]]:
    app_config = _find_project_app_config(app_label)
    models_info = []
    for model in app_config.get_models():
        forward_fields_count = len(
            [field for field in model._meta.get_fields() if not (field.auto_created and not field.concrete)]
        )
        models_info.append(
            {
                "name": model.__name__,
                "model_name": model._meta.model_name,
                "db_table": model._meta.db_table,
                "description": _model_description(model),
                "fields_count": forward_fields_count,
            }
        )
    return sorted(models_info, key=lambda model_info: model_info["name"].lower())


def _related_target(related_model: Any) -> dict[str, str] | None:
    if not related_model or not hasattr(related_model, "_meta"):
        return None
    return {
        "app_label": related_model._meta.app_label,
        "model_name": related_model._meta.model_name,
        "label": related_model._meta.label,
    }


def _forward_fields(model: type[Model]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for field in model._meta.get_fields():
        if field.auto_created and not field.concrete:
            continue
        related_target = _related_target(getattr(field, "related_model", None)) if field.is_relation else None
        description = _field_description(field)
        fields.append(
            {
                "name": field.name,
                "type": _field_type(field),
                "description": description,
                "has_description": description != tr(NO_DESCRIPTION),
                "is_relation": bool(related_target),
                "related_target": related_target,
            }
        )
    return sorted(fields, key=lambda field: field["name"].lower())


def _reverse_relations(model: type[Model]) -> list[dict[str, Any]]:
    relations: list[dict[str, Any]] = []
    for relation in model._meta.get_fields():
        if not (relation.auto_created and not relation.concrete and relation.is_relation):
            continue

        source_model = getattr(relation, "related_model", None)
        source_target = _related_target(source_model)
        if not source_target:
            continue

        source_field = getattr(relation, "field", None)
        source_field_name = getattr(source_field, "name", relation.name)
        accessor_name = relation.get_accessor_name() if hasattr(relation, "get_accessor_name") else relation.name

        relations.append(
            {
                "name": accessor_name,
                "type": _field_type(relation),
                "description": _pick_description(
                    getattr(source_field, "help_text", ""),
                    tr(
                        "[Field %(field_name)s of model %(model_label)s]",
                        field_name=source_field_name,
                        model_label=source_model._meta.label,
                    ),
                ),
                "source_field_name": source_field_name,
                "source_model_label": source_model._meta.label,
                "source_target": source_target,
            }
        )
    return sorted(
        relations,
        key=lambda relation: (
            relation["source_model_label"].lower(),
            relation["source_field_name"].lower(),
        ),
    )


def _find_model(app_label: str, model_name: str) -> type[Model]:
    app_config = _find_project_app_config(app_label)
    lookup = model_name.lower()
    for model in app_config.get_models():
        if model._meta.model_name == lookup or model.__name__.lower() == lookup:
            return model
    raise LookupError(
        tr("[Model not found: %(app_label)s.%(model_name)s]", app_label=app_label, model_name=model_name)
    )


def get_model_details(app_label: str, model_name: str) -> dict[str, Any]:
    model = _find_model(app_label, model_name)
    return {
        "app_label": model._meta.app_label,
        "model_name": model._meta.model_name,
        "model_label": model._meta.label,
        "db_table": model._meta.db_table,
        "description": _model_detail_description(model),
        "fields": _forward_fields(model),
        "reverse_relations": _reverse_relations(model),
    }
