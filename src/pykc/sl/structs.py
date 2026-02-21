import functools
from collections.abc import Callable
from typing import (
    Any,
    TypeVar,
)

import sqlalchemy as sa

# Named types to allow switching to a TypedDict or Dataclass later if desired.
type MemberStruct = dict[str, Any]
type ApiTokenStruct = dict[str, Any]
type VenueStruct = dict[str, Any]
type RecurringStruct = dict[str, Any]
type EventStruct = dict[str, Any]


STRUCT = TypeVar("STRUCT", MemberStruct, EventStruct, VenueStruct, RecurringStruct)

member_mapping = {
    "id": "member_id",
    "permissions": "member_permissions",
    "moniker": "member_moniker",
    "first_name": "member_first_name",
    "last_name": "member_last_name",
    "pronouns": "member_pronouns",
}

api_token_mapping = {
    "id": "member_id",
    "hash": "api_token_hash",
    "jwt": "api_token_jwt",
    "revoked": "api_token_revoked",
}


venue_mapping = {
    "id": "venue_id",
    "name": "venue_name",
    "city": "venue_city",
    "state": "venue_state",
    "address_line1": "venue_address_line1",
    "address_line2": "venue_address_line2",
    "address_line3": "venue_address_line3",
    "postal_code": "venue_postal_code",
    "external_link": "venue_external_link",
}

recurring_mapping = {
    "id": "recurring_id",
    "title": "recurring_title",
    "description": "recurring_description",
    "interval_type": "recurring_interval_type",
    "month": "recurring_month",
    "week": "recurring_week",
    "day": "recurring_day",
    "start_time": "recurring_start_time",
    "end_time": "recurring_end_time",
}

event_mapping = {
    "id": "event_id",
    "title": "event_title",
    "description": "event_description",
    "external_link": "event_external_link",
    "start": "event_start",
    "end": "event_end",
    "is_cancelled": "event_is_cancelled",
    "recurring_id": "event_recurring_id",
    "venue_id": "event_venue_id",
    "location_details": "event_location_details",
    "is_av_capable": "event_is_av_capable",
    "recurring_interval_type": "recurring_interval_type",
    "recurring_month": "recurring_month",
    "recurring_week": "recurring_week",
    "recurring_day": "recurring_day",
    "recurring_start_time": "recurring_start_time",
    "recurring_end_time": "recurring_end_time",
    "venue_name": "venue_name",
    "venue_city": "venue_city",
    "venue_state": "venue_state",
    "venue_address_line1": "venue_address_line1",
    "venue_address_line2": "venue_address_line2",
    "venue_address_line3": "venue_address_line3",
    "venue_postal_code": "venue_postal_code",
    "venue_external_link": "venue_external_link",
}


def build_struct(field_mapping: dict[str, str], row: sa.Row) -> Any:
    result = row._tuple()
    return {v: getattr(result, k) for k, v in field_mapping.items()}


member_struct: Callable[[sa.Row], MemberStruct] = functools.partial(build_struct, member_mapping)
api_token_struct: Callable[[sa.Row], ApiTokenStruct] = functools.partial(
    build_struct, api_token_mapping
)
venue_struct: Callable[[sa.Row], VenueStruct] = functools.partial(build_struct, venue_mapping)
recurring_struct: Callable[[sa.Row], RecurringStruct] = functools.partial(
    build_struct, recurring_mapping
)
event_struct: Callable[[sa.Row], EventStruct] = functools.partial(build_struct, event_mapping)


struct_factory = {
    "member": member_struct,
    "venue": venue_struct,
    "recurring": recurring_struct,
    "event": event_struct,
    "api_token": api_token_struct,
}


def build_raw[
    S: (
        MemberStruct,
        ApiTokenStruct,
        VenueStruct,
        RecurringStruct,
        EventStruct,
    )
](field_mapping: dict[str, str], struct_data: S) -> dict[str, Any]:
    return {k: struct_data[v] for k, v in field_mapping.items() if v in struct_data}


member_raw: Callable[[MemberStruct], dict[str, Any]] = functools.partial(build_raw, member_mapping)
api_token_raw: Callable[[ApiTokenStruct], dict[str, Any]] = functools.partial(
    build_raw, api_token_mapping
)
venue_raw: Callable[[VenueStruct], dict[str, Any]] = functools.partial(build_raw, venue_mapping)
recurring_raw: Callable[[RecurringStruct], dict[str, Any]] = functools.partial(
    build_raw, recurring_mapping
)
event_raw: Callable[[EventStruct], dict[str, Any]] = functools.partial(build_raw, event_mapping)


raw_factory = {
    "member": member_raw,
    "api_token": api_token_raw,
    "venue": venue_raw,
    "recurring": recurring_raw,
    "event": event_raw,
}
