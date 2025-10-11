import functools
from collections.abc import Awaitable
from typing import (
    Any,
    Protocol,
)

import sqlalchemy as sa
from grammdb import (
    delete,
    insert,
    update,
)
from sqlalchemy.ext.asyncio import AsyncConnection

from pykc.dl import where
from pykc.types import PK


class CreateFunction(Protocol):
    def __call__(self, tr: AsyncConnection, **kwargs: Any) -> Awaitable[PK]: ...


class UpdateFunction(Protocol):
    def __call__(self, tr: AsyncConnection, id: PK, **kwargs: Any) -> Awaitable[PK]: ...


class DeleteFunction(Protocol):
    def __call__(self, tr: AsyncConnection, id: PK) -> Awaitable[PK]: ...


def make_create(table_class: sa.Table) -> CreateFunction:
    return functools.partial(_create, table_class)


def make_update(table_class: sa.Table) -> UpdateFunction:
    return functools.partial(_edit_by_id, table_class)


def make_delete(table_class: sa.Table) -> UpdateFunction:
    return functools.partial(_remove_by_id, table_class)


async def _create(table_class: sa.Table, tr: AsyncConnection, **kwargs) -> PK:
    stmt = insert(into=table_class, **kwargs).returning(table_class.c.id)
    res = await tr.execute(stmt)
    return res.scalar_one()


async def _edit_by_id(table_class: sa.Table, tr: AsyncConnection, id: PK, **kwargs) -> PK:
    stmt = update(table_class, where.id_is(table_class, id), **kwargs).returning(table_class.c.id)
    res = await tr.execute(stmt)
    return res.scalar_one()


async def _remove_by_id(table_class: sa.Table, tr: AsyncConnection, id: PK) -> PK:
    stmt = delete(table_class, where.id_is(table_class, id)).returning(table_class.c.id)
    res = await tr.execute(stmt)
    return res.scalar_one()
