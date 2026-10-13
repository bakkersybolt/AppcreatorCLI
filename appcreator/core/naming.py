"""Naming helpers for AppCreator: slugs, Python package names and app name validation."""

import re
from typing import Optional

APP_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9 _-]*$")


def make_slug(app_naam: str) -> str:
    """Returns the kebab-case slug used for project, container and distribution names."""
    return app_naam.strip().lower().replace(" ", "-").replace("_", "-")


def make_package_name(app_naam: str) -> str:
    """Returns a valid Python package name (snake_case) derived from the app name."""
    return make_slug(app_naam).replace("-", "_")


def validate_app_name(app_naam: str) -> Optional[str]:
    """Returns a Dutch error message if the app name is invalid, otherwise None."""
    if not app_naam or not app_naam.strip():
        return "Geen applicatienaam opgegeven."
    if not APP_NAME_PATTERN.match(app_naam.strip()):
        return (
            "Ongeldige applicatienaam. Begin met een letter en gebruik alleen letters, "
            "cijfers, spaties, '-' en '_'."
        )
    return None
