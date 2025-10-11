import functools

import sqlalchemy as sa
from grammdb.types import WhereFunc

from pykc.common import timestamps
from pykc.constants import TIMEZONE
from pykc.dl import tables
from pykc.types import PK


def id_is(table_class: sa.Table, id: PK) -> WhereFunc:
    def _(selectable):
        return selectable.where(table_class.c.id == id)

    return _


member_id_is = functools.partial(id_is, tables.Member)
event_id_is = functools.partial(id_is, tables.Event)
venue_id_is = functools.partial(id_is, tables.Venue)
recurring_id_is = functools.partial(id_is, tables.Recurring)


def discord_id_is(discord_id: str) -> WhereFunc:
    def _(selectable):
        return selectable.where(tables.Member.c.discord_id == discord_id)

    return _


def moniker_is(moniker: str) -> WhereFunc:
    def _(selectable):
        return selectable.where(tables.Member.c.moniker == moniker)

    return _


def moniker_like(moniker: str) -> WhereFunc:
    def _(selectable):
        return selectable.where(tables.Member.c.moniker.like(f"%{moniker}%"))

    return _


def title_like(title: str) -> WhereFunc:
    def _(selectable):
        return selectable.where(tables.Event.c.title.like(f"%{title}%"))

    return _


def has_permission(permission_bit: int) -> WhereFunc:
    def _(selectable):
        return selectable.where(tables.Member.c.permissions & permission_bit)

    return _


def token_hash_is(token_hash: str) -> WhereFunc:
    def _(selectable):
        return selectable.where(tables.ApiToken.c.hash == token_hash)

    return _


def token_is_not_revoked() -> WhereFunc:
    def _(selectable):
        return selectable.where(tables.ApiToken.c.revoked == False)

    return _


def is_cancelled() -> WhereFunc:
    def _(selectable):
        return selectable.where(tables.Event.c.is_cancelled == True)

    return _


def is_not_cancelled() -> WhereFunc:
    def _(selectable):
        return selectable.where(tables.Event.c.is_cancelled == False)

    return _


def is_upcoming() -> WhereFunc:
    def _(selectable):
        return selectable.where(tables.Event.c.start > timestamps.now().astimezone(TIMEZONE))

    return _


def is_past() -> WhereFunc:
    def _(selectable):
        return selectable.where(tables.Event.c.start <= timestamps.today())

    return _


def is_latest_start_date() -> WhereFunc:
    def _(selectable):
        return selectable.where(sa.func.max(tables.Event.c.start))

    return _
