#!/usr/bin/env python3
"""Commande de gestion Django."""

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django n'est pas installe. Installez les dependances avant d'executer cette commande."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
