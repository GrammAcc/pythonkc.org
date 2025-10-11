__all__ = [
    "events",
    "init",
    "members",
]
import functools
import os
from collections.abc import Callable

from grammdb import (
    db_factory,
    init_db,
)
from grammdb.contracts import DatabaseModule

from pykc.dl import schemas

members: Callable[[], DatabaseModule] = db_factory(schemas.members)
events: Callable[[], DatabaseModule] = db_factory(schemas.events)
init = functools.partial(
    init_db, hook=schemas.helpers.enable_sqlite_fks, echo=bool(os.environ.get("DEBUG", False))
)
