__all__ = [
    "acl",
    "errors",
    "fetch",
    "init_app",
    "pubsub",
    "scheduling",
    "structs",
    "tokens",
]

import os

from pykc.constants import App
from pykc.dl import db

from . import (
    acl,
    errors,
    pubsub,
    scheduling,
    structs,
    tokens,
)


async def _init_members() -> None:
    members_db_uri = os.environ["MEMBERS_DB_URI"]
    await db.init(db.members(), members_db_uri, drop_tables=False)


async def _init_events() -> None:
    events_db_uri = os.environ["EVENTS_DB_URI"]
    await db.init(db.events(), events_db_uri, drop_tables=False)


_dispatch = {
    App.MEMBERS: _init_members,
    App.EVENTS: _init_events,
}


async def init_app(app_bit: App) -> None:
    if app_bit not in _dispatch:
        raise ValueError(f"Cannot initialize invalid app specifier ${app_bit}")
    await _dispatch[app_bit]()
