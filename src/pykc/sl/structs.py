import datetime
from typing import (
    Any,
    TypeVar,
)

import sqlalchemy as sa

# Named type to allow switching to a TypedDict or Dataclass later if desired.
type MemberStruct = dict[str, Any]


def member_struct(row: sa.Row) -> MemberStruct:
    result = row._tuple()
    return {
        "member_id": result.member_id,
        "member_permissions": result.member_permissions,
        "member_moniker": result.member_moniker,
        "member_first_name": result.member_first_name,
        "member_last_name": result.member_last_name,
        "member_pronouns": result.member_pronouns,
    }


# Named type to allow switching to a TypedDict or Dataclass later if desired.
type VenueStruct = dict[str, Any]


def venue_struct(row: sa.Row) -> VenueStruct:
    result = row._tuple()
    return {
        "venue_id": result.venue_id,
        "venue_name": result.venue_name,
        "venue_city": result.venue_city,
        "venue_state": result.venue_state,
        "venue_address_line1": result.venue_address_line1,
        "venue_address_line2": result.venue_address_line2,
        "venue_address_line3": result.venue_address_line3,
        "venue_postal_code": result.venue_postal_code,
        "venue_external_link": result.venue_external_link,
    }


# Named type to allow switching to a TypedDict or Dataclass later if desired.
type RecurringStruct = dict[str, Any]


def recurring_struct(row: sa.Row) -> RecurringStruct:
    result = row._tuple()
    return {
        "recurring_id": result.recurring_id,
        "recurring_title": result.recurring_title,
        "recurring_description": result.recurring_description,
        "recurring_interval_type": result.recurring_interval_type,
        "recurring_month": result.recurring_month,
        "recurring_week": result.recurring_week,
        "recurring_day": result.recurring_day,
        "recurring_start_time": result.recurring_start_time,
        "recurring_end_time": result.recurring_end_time,
    }


# Named type to allow switching to a TypedDict or Dataclass later if desired.
type EventStruct = dict[str, Any]


def event_struct(row: sa.Row) -> EventStruct:
    result = row._tuple()
    return {
        "event_id": result.event_id,
        "event_title": result.event_title,
        "event_description": result.event_description,
        "event_external_link": result.event_external_link,
        "event_date": result.event_start.date(),
        "event_start_time": result.event_start.time(),
        "event_end_time": result.event_end.time(),
        "event_is_cancelled": result.event_is_cancelled,
        "event_recurring_id": result.event_recurring_id,
        "event_venue_id": result.event_venue_id,
        "event_location_details": result.event_location_details,
        "event_is_av_capable": result.event_is_av_capable,
        "recurring_id": result.recurring_id,
        "recurring_interval_type": result.recurring_interval_type,
        "recurring_month": result.recurring_month,
        "recurring_week": result.recurring_week,
        "recurring_day": result.recurring_day,
        "recurring_start_time": result.recurring_start_time,
        "recurring_end_time": result.recurring_end_time,
        "venue_id": result.venue_id,
        "venue_name": result.venue_name,
        "venue_city": result.venue_city,
        "venue_state": result.venue_state,
        "venue_address_line1": result.venue_address_line1,
        "venue_address_line2": result.venue_address_line2,
        "venue_address_line3": result.venue_address_line3,
        "venue_postal_code": result.venue_postal_code,
        "venue_external_link": result.venue_external_link,
    }


STRUCT = TypeVar("STRUCT", MemberStruct, EventStruct, VenueStruct, RecurringStruct)


def member_raw(struct_data: STRUCT) -> dict[str, Any]:
    return {k.removeprefix("member_"): v for k, v in struct_data.items() if k.startswith("member_")}


def recurring_raw(struct_data: STRUCT) -> dict[str, Any]:
    return {
        k.removeprefix("recurring_"): v
        for k, v in struct_data.items()
        if k.startswith("recurring_")
    }


def venue_raw(struct_data: STRUCT) -> dict[str, Any]:
    return {k.removeprefix("venue_"): v for k, v in struct_data.items() if k.startswith("venue_")}


# [[fr]]Rename::dict[str, Any]::RawData[[fr]]
def event_raw(struct_data: STRUCT) -> dict[str, Any]:
    overrides = ["event_date", "event_start_time", "event_end_time"]

    result = {
        k.removeprefix("event_"): v
        for k, v in struct_data.items()
        if k.startswith("event_") and k not in overrides
    }
    override_results = {
        "start": datetime.datetime.combine(
            struct_data["event_date"], struct_data["event_start_time"]
        ),
        "end": datetime.datetime.combine(struct_data["event_date"], struct_data["event_end_time"]),
    }
    return {**result, **override_results}
