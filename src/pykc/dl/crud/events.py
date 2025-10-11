import datetime

import sqlalchemy as sa
from grammdb import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncResult,
)

from pykc.dl import (
    from_,
    tables,
    where,
)
from pykc.types import PK

from .factories import (
    make_create,
    make_delete,
    make_update,
)


async def search_events(tr: AsyncConnection, search_query: str) -> AsyncResult:
    # TODO: Include description and venue name in search.
    stmt = select(
        "*", from_.events(), where.is_upcoming(), where.title_like(search_query)
    ).order_by(tables.Event.c.start.desc())
    rows = await tr.stream(stmt)
    return rows


async def get_events(tr: AsyncConnection) -> AsyncResult:
    stmt = select("*", from_.events())
    rows = await tr.stream(stmt)
    return rows


async def get_venues(tr: AsyncConnection) -> AsyncResult:
    stmt = select("*", from_.venues()).order_by(tables.Venue.c.name.asc())
    rows = await tr.stream(stmt)
    return rows


async def get_event_by_id(tr: AsyncConnection, event_id: PK) -> sa.Row:
    stmt = select("*", from_.events(), where.event_id_is(event_id))
    event = await tr.execute(stmt)
    return event.one()


async def get_upcoming_events_by_recurring_id(tr: AsyncConnection, recurring_id: PK) -> AsyncResult:
    # Tech Debt Note: Gramm is too stupid to use subqueries properly.
    stmt = select(
        "*", from_.events(), where.recurring_id_is(recurring_id), where.is_upcoming()
    ).order_by(tables.Event.c.start.asc())
    events = await tr.stream(stmt)
    return events


async def get_next_recurring_event(tr: AsyncConnection, recurring_id: PK) -> sa.Row:
    # Tech Debt Note: Gramm is too stupid to use subqueries properly.
    stmt = select(
        "*", from_.events(), where.recurring_id_is(recurring_id), where.is_upcoming()
    ).order_by(tables.Event.c.start.asc())
    events = await tr.execute(stmt)
    res = events.first()
    assert res is not None
    return res


async def get_latest_recurring_event(tr: AsyncConnection, recurring_id: PK) -> sa.Row:
    # Tech Debt Note: Gramm is too stupid to use subqueries properly.
    stmt = select(
        "*", from_.events(), where.recurring_id_is(recurring_id), where.is_upcoming()
    ).order_by(tables.Event.c.start.desc())
    events = await tr.execute(stmt)
    res = events.first()
    assert res is not None
    return res


async def get_cancelled_events(tr: AsyncConnection) -> AsyncResult:
    stmt = select("*", from_.events(), where.is_cancelled()).order_by(tables.Event.c.start.asc())
    rows = await tr.stream(stmt)
    return rows


async def get_upcoming_events(tr: AsyncConnection) -> AsyncResult:
    stmt = select("*", from_.events(), where.is_upcoming()).order_by(tables.Event.c.start.asc())
    rows = await tr.stream(stmt)
    return rows


async def get_past_events(tr: AsyncConnection) -> AsyncResult:
    stmt = select("*", from_.events(), where.is_past()).order_by(tables.Event.c.start.desc())
    rows = await tr.stream(stmt)
    return rows


async def get_venue_by_id(tr: AsyncConnection, venue_id: PK) -> sa.Row:
    stmt = select("*", from_.venues(), where.venue_id_is(venue_id))
    venue = await tr.execute(stmt)
    return venue.one()


async def get_recurrings(tr: AsyncConnection) -> AsyncResult:
    stmt = select("*", from_.recurring()).order_by(tables.Recurring.c.interval_type.asc())
    rows = await tr.stream(stmt)
    return rows


async def get_recurring_by_id(tr: AsyncConnection, recurring_id: PK) -> sa.Row:
    stmt = select("*", from_.recurring(), where.recurring_id_is(recurring_id))
    recurring = await tr.execute(stmt)
    return recurring.one()


async def get_latest_event_date(tr: AsyncConnection, recurring_id: PK) -> datetime.date | None:
    stmt = select(
        "event_start_date",
        from_.events(),
        where.recurring_id_is(recurring_id),
        where.is_latest_start_date(),
    )
    latest_event = await tr.execute(stmt)
    try:
        return latest_event.scalar_one()
    except NoResultFound:
        return None


create_event = make_create(tables.Event)
create_recurring = make_create(tables.Recurring)
create_venue = make_create(tables.Venue)
update_event = make_update(tables.Event)
update_recurring = make_update(tables.Recurring)
update_venue = make_update(tables.Venue)
delete_event = make_delete(tables.Event)
delete_recurring = make_delete(tables.Recurring)
delete_venue = make_delete(tables.Venue)
