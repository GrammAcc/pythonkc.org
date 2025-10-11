import functools
import os
import string
from typing import Any

from pykc.constants import App


def hyphen_to_snake(s: str) -> str:
    return s.replace("-", "_")


def snake_to_hyphen(s: str) -> str:
    return s.replace("_", "-")


def map_enum_members(enum_class: Any) -> list[tuple[str, Any]]:
    return [(" ".join(string.capwords(i.name, "_").split("_")), i.value) for i in enum_class]


def get_domain() -> str:
    """Return the full domain name and scheme identifier for the api without
    a quart application context.
    """

    return os.environ["SITE_ROOT"]


def get_site_root() -> str:
    """Return the full base url for the site without a quart application context."""

    return (os.environ["SITE_ROOT"] + os.environ["BASE_URL"]).strip("/")


def get_enabled_apps() -> int:
    enabled_apps_override = os.environ.get("ENABLED_APPS", None)
    if enabled_apps_override is not None:
        return int(enabled_apps_override)
    else:
        return functools.reduce(lambda acc, bit: acc | bit, list(App), 0)


def is_app_enabled(app_bit: int) -> bool:
    return bool(get_enabled_apps() & app_bit)
