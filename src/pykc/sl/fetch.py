import grammdb

from pykc.constants import MemberRoles
from pykc.dl import (
    crud,
    db,
)
from pykc.sl import structs
from pykc.sl.structs import (
    EventStruct,
    MemberStruct,
    RecurringStruct,
    VenueStruct,
)
from pykc.types import PK


async def search_members(query: str) -> list[MemberStruct]:
    async with grammdb.connection_ctx(db.members()) as tr:
        res = await crud.search_members(tr, query)
        return [structs.member_struct(i) async for i in res]


async def search_events(query: str) -> list[EventStruct]:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.search_events(tr, query)
        return [structs.event_struct(i) async for i in res]


async def members() -> list[MemberStruct]:
    async with grammdb.connection_ctx(db.members()) as tr:
        res = await crud.get_members(tr)
        return [structs.member_struct(i) async for i in res]


async def member_by_id(member_id: PK) -> MemberStruct:
    async with grammdb.connection_ctx(db.members()) as tr:
        res = await crud.get_member_by_id(tr, member_id)
        return structs.member_struct(res)


async def member_by_moniker(moniker: str) -> MemberStruct:
    async with grammdb.connection_ctx(db.members()) as tr:
        res = await crud.get_member_by_moniker(tr, moniker)
        await grammdb.close_transaction(tr)
        return structs.member_struct(res)


async def member_by_discord_id(discord_id: str) -> MemberStruct:
    async with grammdb.connection_ctx(db.members()) as tr:
        res = await crud.get_member_by_discord_id(tr, discord_id)
        return structs.member_struct(res)


async def member_permissions(member_id: PK) -> MemberRoles:
    async with grammdb.connection_ctx(db.members()) as tr:
        return await crud.get_member_permissions(tr, member_id)


async def events() -> list[EventStruct]:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.get_events(tr)
        return [structs.event_struct(r) async for r in res]


async def venues() -> list[VenueStruct]:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.get_venues(tr)
        return [structs.venue_struct(r) async for r in res]


async def event_by_id(event_id: PK) -> EventStruct:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.get_event_by_id(tr, event_id)
        return structs.event_struct(res)


async def upcoming_recurring_events(recurring_id: PK) -> list[EventStruct]:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.get_upcoming_events_by_recurring_id(tr, recurring_id)
        return [structs.event_struct(r) async for r in res]


async def next_event_by_recurring_id(recurring_id: PK) -> EventStruct:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.get_next_recurring_event(tr, recurring_id)
        return structs.event_struct(res)


async def latest_event_by_recurring_id(recurring_id: PK) -> EventStruct:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.get_latest_recurring_event(tr, recurring_id)
        return structs.event_struct(res)


async def recurrings() -> list[RecurringStruct]:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.get_recurrings(tr)
        return [structs.recurring_struct(r) async for r in res]


async def venue_by_id(venue_id: PK) -> EventStruct:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.get_venue_by_id(tr, venue_id)
        return structs.venue_struct(res)


async def recurring_by_id(recurring_id: PK) -> RecurringStruct:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.get_recurring_by_id(tr, recurring_id)
        return structs.recurring_struct(res)


async def upcoming_events() -> list[EventStruct]:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.get_upcoming_events(tr)
        return [structs.event_struct(r) async for r in res]


async def past_events() -> list[EventStruct]:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.get_past_events(tr)
        return [structs.event_struct(r) async for r in res]
