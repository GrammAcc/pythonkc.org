__all__ = [
    "register_routes",
]

from . import (
    api,
    live,
    pages,
)


def register_routes():
    pages.register_routes()
    api.register_routes()
    live.register_routes()
