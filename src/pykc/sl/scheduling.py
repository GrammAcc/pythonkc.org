import datetime

import grammdb

from pykc.constants import EventIntervalType
from pykc.dl import (
    crud,
    db,
)
from pykc.sl import structs
from pykc.sl.structs import (
    EventStruct,
    RecurringStruct,
    VenueStruct,
)
from pykc.types import (
    PK,
    RawData,
)


def _get_day_index(recurring_event: RecurringStruct) -> int:
    if recurring_event["recurring_interval_type"] < EventIntervalType.MONTHLY:
        return recurring_event["recurring_day"]
    else:
        return ((recurring_event["recurring_week"] - 1) * 7) + recurring_event["recurring_day"]


def _get_month_index(recurring_event: RecurringStruct) -> int:
    if recurring_event["recurring_interval_type"] > EventIntervalType.MONTHLY:
        return recurring_event["recurring_month"]
    else:
        return datetime.date.today().month


async def delete_recurring(recurring_id: PK) -> tuple[PK, PK]:
    async with grammdb.connection_ctx(db.events()) as tr:
        # Cancel any scheduled event for this recurring series before deleting the FK.
        event_id = (await crud.get_next_recurring_event(tr, recurring_id)).event_id
        await crud.update_event(tr, event_id, is_cancelled=True)
        deleted_id = await crud.delete_recurring(tr, recurring_id)
        await grammdb.commit_transaction(tr)
        return deleted_id, event_id


async def update_recurring(recurring_id: PK, **new_values) -> RecurringStruct:
    async with grammdb.connection_ctx(db.events()) as tr:
        await crud.update_recurring(tr, id=recurring_id, **structs.recurring_raw(new_values))
        scheduled_events = await crud.get_upcoming_events_by_recurring_id(tr, recurring_id)
        anchor_date = datetime.date.today()
        async for event in scheduled_events:
            new_event_date = compute_next_event_date(new_values, anchor_date)
            new_event_start = datetime.datetime.combine(
                new_event_date, new_values["recurring_start_time"]
            )
            new_event_end = datetime.datetime.combine(
                new_event_date, new_values["recurring_end_time"]
            )
            await crud.update_event(tr, event.event_id, start=new_event_start, end=new_event_end)
            anchor_date = new_event_date
        res = await crud.get_recurring_by_id(tr, recurring_id)
        await grammdb.commit_transaction(tr)
        return structs.recurring_struct(res)


def _compute_month_and_year(proposed: datetime.date, month_offset: int) -> tuple[int, int]:
    """Compute the month incremented by an offset and rolling over the year if needed.

    Returns a 2-tuple where the first element is the absolute year value and the second is
    the absolute month value.
    """

    if (proposed_month := proposed.month + month_offset) > 12:
        return proposed.year + 1, proposed_month % 12
    else:
        return proposed.year, proposed_month


def _compute_date_of_month(
    start_of_month: datetime.date, recurring_week: int, recurring_day: int
) -> datetime.date:
    calendar = start_of_month.isocalendar()
    # Logic Explanation:
    # If the first of the month is before the target day of the week, then we reduce the
    # offset by 1.
    #
    # For example, target day is Thursday and first day of the month is a Tuesday:
    #   The current week is 20, and the user specified the third Thursday. We need to offset the
    #   week +2 to get the third Thursday since the current week includes a Thursday in this month.
    #   If the first day of the month was a Saturday, then we would need to offset the week +3
    #   since there is no Thursday in this month as part of the current week.
    week_offset = recurring_week - 1 if calendar.weekday <= recurring_day else recurring_week

    return datetime.date.fromisocalendar(
        year=calendar.year, week=calendar.week + week_offset, day=recurring_day
    )


def compute_next_event_date(
    recurring_event: RecurringStruct, anchor_date: datetime.date
) -> datetime.date:
    match {k.removeprefix("recurring_"): v for k, v in recurring_event.items()}:
        case {"interval_type": EventIntervalType.DAILY}:
            return anchor_date + datetime.timedelta(days=1)

        case {"interval_type": EventIntervalType.WEEKLY, "day": int(day)}:
            cal = anchor_date.isocalendar()
            proposed = datetime.date.fromisocalendar(year=cal.year, week=cal.week, day=day)
            if proposed > anchor_date:
                return proposed
            else:
                return proposed + datetime.timedelta(days=7)

        case {
            "interval_type": EventIntervalType.YEARLY,
            "month": int(month),
            "week": int(week),
            "day": int(day),
        }:
            start_of_month = anchor_date.replace(month=month, day=1)
            proposed = _compute_date_of_month(start_of_month, week, day)
            if proposed > anchor_date:
                return proposed
            else:
                next_year_start_of_month = proposed.replace(year=proposed.year + 1, day=1)
                return _compute_date_of_month(next_year_start_of_month, week, day)

        case {"interval_type": modulus, "week": int(week), "day": int(day)}:
            if (rem := anchor_date.month % modulus) > 0:
                year, month = _compute_month_and_year(anchor_date, modulus - rem)
            else:
                year, month = anchor_date.year, anchor_date.month
            start_of_month = anchor_date.replace(year=year, month=month, day=1)
            proposed = _compute_date_of_month(start_of_month, week, day)
            if proposed > anchor_date:
                return proposed
            else:
                incremented_year, incremented_month = _compute_month_and_year(proposed, modulus)
                start_of_next_month = proposed.replace(
                    year=incremented_year, month=incremented_month, day=1
                )
                return _compute_date_of_month(start_of_next_month, week, day)
        case _:
            raise ValueError("Invalid Struct")


async def create_venue(*, venue_data: RawData) -> PK:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.create_venue(tr, **structs.venue_raw(venue_data))
        await grammdb.commit_transaction(tr)
        return res


async def update_venue(venue_id: PK, **new_values) -> VenueStruct:
    async with grammdb.connection_ctx(db.events()) as tr:
        await crud.update_venue(tr, id=venue_id, **structs.venue_raw(new_values))
        res = await crud.get_venue_by_id(tr, venue_id)
        await grammdb.commit_transaction(tr)
        return structs.venue_struct(res)


async def delete_venue(venue_id: PK) -> PK:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.delete_venue(tr, venue_id)
        await grammdb.commit_transaction(tr)
        return res


async def create_recurring(*, recurring_data: RawData) -> PK:
    async with grammdb.connection_ctx(db.events()) as tr:
        raw_data = structs.recurring_raw(recurring_data)
        recurring_id = await crud.create_recurring(tr, **raw_data)
        event_date = compute_next_event_date(recurring_data, datetime.date.today())
        event_start = datetime.datetime.combine(event_date, recurring_data["recurring_start_time"])
        event_end = datetime.datetime.combine(event_date, recurring_data["recurring_end_time"])
        event_data = {
            "title": raw_data["title"],
            "description": raw_data["description"],
            "recurring_id": recurring_id,
            "start": event_start,
            "end": event_end,
        }

        await crud.create_event(tr, **event_data)
        await grammdb.commit_transaction(tr)
        return recurring_id


async def schedule_next_event(recurring_data: RecurringStruct, anchor_date: datetime.date) -> PK:
    async with grammdb.connection_ctx(db.events()) as tr:
        event_date = compute_next_event_date(recurring_data, anchor_date)
        event_start = datetime.datetime.combine(event_date, recurring_data["recurring_start_time"])
        event_end = datetime.datetime.combine(event_date, recurring_data["recurring_end_time"])
        event_data = {
            "title": recurring_data["recurring_title"],
            "description": recurring_data["recurring_description"],
            "recurring_id": recurring_data["recurring_id"],
            "start": event_start,
            "end": event_end,
        }

        event_id = await crud.create_event(tr, **event_data)
        await grammdb.commit_transaction(tr)
        return event_id


async def create_event(*, event_data: RawData) -> PK:
    async with grammdb.connection_ctx(db.events()) as tr:
        event_id = await crud.create_event(tr, **structs.event_raw(event_data))
        await grammdb.commit_transaction(tr)
        return event_id


async def update_event(event_id: PK, **new_values) -> EventStruct:
    async with grammdb.connection_ctx(db.events()) as tr:
        await crud.update_event(tr, event_id, **structs.event_raw(new_values))
        res = await crud.get_event_by_id(tr, event_id)
        await grammdb.commit_transaction(tr)
        return structs.event_struct(res)


async def cancel_event(event_id: PK) -> PK:
    async with grammdb.connection_ctx(db.events()) as tr:
        canceled_id = await crud.update_event(tr, event_id, is_cancelled=True)
        await grammdb.commit_transaction(tr)
        return canceled_id


async def delete_event(event_id: PK) -> PK:
    async with grammdb.connection_ctx(db.events()) as tr:
        res = await crud.delete_event(tr, event_id)
        await grammdb.commit_transaction(tr)
        return res
