import datetime
import functools
from typing import Any

from pykc.constants import EventIntervalType
from pykc.types import RawData

from .validation.constants import INVALID_SENTINAL
from .validation.contracts import (
    TransformFunc,
    TransformTable,
)
from .validation.transforms import *
from .validation.validations import *

_fallback_to_empty_str = functools.partial(fallback, "")


def _required_if_provided(fname: str, next_stage: TransformFunc):
    return required_if((lambda f, msg: msg.get(fname) is not None), next_stage)


CreateMember = TransformTable(
    "member",
    sanitize={
        "member_moniker": required(noop),
        "member_discord_id": required(noop),
        "member_first_name": optional(noop),
        "member_last_name": optional(noop),
        "member_pronouns": optional(noop),
    },
    prepare={
        "member_moniker": noop,
        "member_discord_id": noop,
        "member_first_name": fallback("", noop),
        "member_last_name": fallback("", noop),
        "member_pronouns": fallback("", noop),
    },
)


CreateMemberFromDiscord = TransformTable(
    "member",
    sanitize={
        "member_moniker": read_first_field(
            ["global_name", "username"], required(coerce_str(transform))
        ),
        "member_discord_id": read_field("id", required(coerce_str(transform))),
    },
    prepare={
        "member_moniker": noop,
        "member_discord_id": noop,
    },
)


DiscordLogin = TransformTable(
    "member",
    sanitize={
        "code": required(noop),
        "state": required(noop),
    },
    prepare={
        "code": noop,
        "state": noop,
    },
)

UpdateMember = TransformTable(
    "member",
    sanitize={
        "member_moniker": required(noop),
        "member_first_name": optional(noop),
        "member_last_name": optional(noop),
        "member_pronouns": optional(noop),
    },
    prepare={
        "member_moniker": noop,
        "member_first_name": fallback("", noop),
        "member_last_name": fallback("", noop),
        "member_pronouns": fallback("", noop),
    },
)


UpdateMemberPermissions = TransformTable(
    "member",
    sanitize={
        "member_permissions": required(coerce_int(transform)),
    },
    prepare={
        "member_permissions": noop,
    },
)


CreateVenue = TransformTable(
    "venue",
    sanitize={
        "venue_name": required(noop),
        "venue_city": required(noop),
        "venue_state": required(coerce_str(uppercase(max_len(2, transform)))),
        "venue_postal_code": required(coerce_str(transform)),
        "venue_address_line1": required(noop),
        "venue_address_line2": optional(noop),
        "venue_address_line3": optional(noop),
        "venue_external_link": required(coerce_str(assert_https(transform))),
    },
    prepare={
        "venue_name": noop,
        "venue_city": noop,
        "venue_state": noop,
        "venue_postal_code": noop,
        "venue_address_line1": noop,
        "venue_address_line2": noop,
        "venue_address_line3": noop,
        "venue_external_link": noop,
    },
)

UpdateVenue = TransformTable(
    "venue",
    sanitize={
        "venue_name": required(noop),
        "venue_city": required(noop),
        "venue_state": required(coerce_str(uppercase(max_len(2, transform)))),
        "venue_postal_code": required(coerce_str(transform)),
        "venue_address_line1": required(noop),
        "venue_address_line2": optional(noop),
        "venue_address_line3": optional(noop),
        "venue_external_link": required(coerce_str(assert_https(transform))),
    },
    prepare={
        "venue_name": noop,
        "venue_city": noop,
        "venue_state": noop,
        "venue_postal_code": noop,
        "venue_address_line1": noop,
        "venue_address_line2": fallback("", noop),
        "venue_address_line3": fallback("", noop),
        "venue_external_link": noop,
    },
)


def _yearly(f, msg):
    try:
        transformed = int(msg.get("recurring_interval_type", 0))
    except ValueError:
        transformed = 0

    return transformed == EventIntervalType.YEARLY


def _above_weekly(f, msg):
    try:
        transformed = int(msg.get("recurring_interval_type", 0))
    except ValueError:
        transformed = 0

    return transformed != EventIntervalType.WEEKLY and transformed != EventIntervalType.DAILY


def _above_daily(f, msg):
    try:
        transformed = int(msg.get("recurring_interval_type", 0))
    except ValueError:
        transformed = 0

    return transformed != EventIntervalType.DAILY


_required_if_yearly = functools.partial(required_if, _yearly)
_required_if_above_weekly = functools.partial(required_if, _above_weekly)
_required_if_above_daily = functools.partial(required_if, _above_daily)


def _assert_before_recurring_end_time(next_stage: TransformFunc) -> TransformFunc:
    def _(field: Any, msg: RawData) -> Any:
        try:
            end_time_raw = msg.get("recurring_end_time")
            if end_time_raw is None or end_time_raw == "":
                return INVALID_SENTINAL, "Event End Time is required"
            end_time = datetime.time.fromisoformat(end_time_raw)
            if end_time <= field:
                return INVALID_SENTINAL, "Event Start Time must be before Event End Time"
            else:
                return next_stage(field, msg)
        except Exception:
            return INVALID_SENTINAL, ""

    return _


def _assert_after_recurring_start_time(next_stage: TransformFunc) -> TransformFunc:
    def _(field: Any, msg: RawData) -> Any:
        try:
            start_time = datetime.time.fromisoformat(msg["recurring_start_time"])
            if start_time >= field:
                return INVALID_SENTINAL, "Event End Time must be after Event Start Time"
            else:
                return next_stage(field, msg)
        except Exception:
            return INVALID_SENTINAL, ""

    return _


CreateRecurring = TransformTable(
    "recurring",
    sanitize={
        "recurring_title": required(coerce_str(transform)),
        "recurring_description": required(coerce_str(transform)),
        "recurring_interval_type": required(coerce_int(assert_enum(EventIntervalType, transform))),
        "recurring_month": _required_if_yearly(coerce_int(transform)),
        "recurring_week": _required_if_above_weekly(coerce_int(transform)),
        "recurring_day": _required_if_above_daily(coerce_int(transform)),
        "recurring_start_time": required(str_to_time(_assert_before_recurring_end_time(transform))),
        "recurring_end_time": required(str_to_time(_assert_after_recurring_start_time(transform))),
    },
    prepare={
        "recurring_title": noop,
        "recurring_description": noop,
        "recurring_interval_type": coerce_str(transform),
        "recurring_month": fallback("", coerce_str(transform)),
        "recurring_week": fallback("", coerce_str(transform)),
        "recurring_day": fallback("", coerce_str(transform)),
        "recurring_start_time": time_to_str(transform),
        "recurring_end_time": time_to_str(transform),
        "recurring_interval_summary": read_field(
            "recurring_interval_type", parse_interval_summary(transform)
        ),
        "recurring_next_scheduled_date": compute_next_scheduled_date(format_as_date(transform)),
    },
)

UpdateRecurring = TransformTable(
    "recurring",
    sanitize={
        "recurring_title": required(coerce_str(transform)),
        "recurring_description": required(coerce_str(transform)),
        "recurring_interval_type": required(coerce_int(assert_enum(EventIntervalType, transform))),
        "recurring_month": _required_if_yearly(coerce_int(transform)),
        "recurring_week": _required_if_above_weekly(coerce_int(transform)),
        "recurring_day": _required_if_above_daily(coerce_int(transform)),
        "recurring_start_time": required(str_to_time(transform)),
        "recurring_end_time": required(str_to_time(transform)),
    },
    prepare={
        "recurring_title": noop,
        "recurring_description": noop,
        "recurring_interval_type": coerce_str(transform),
        "recurring_month": fallback("", coerce_str(transform)),
        "recurring_week": fallback("", coerce_str(transform)),
        "recurring_day": fallback("", coerce_str(transform)),
        "recurring_start_time": time_to_str(transform),
        "recurring_end_time": time_to_str(transform),
        "recurring_interval_summary": read_field(
            "recurring_interval_type", parse_interval_summary(transform)
        ),
        "recurring_next_scheduled_date": compute_next_scheduled_date(format_as_date(transform)),
    },
)


def _assert_before_end_time(next_stage: TransformFunc) -> TransformFunc:
    def _(field: Any, msg: RawData) -> Any:
        try:
            end_time_raw = msg.get("event_end_time")
            if end_time_raw is None or end_time_raw == "":
                return INVALID_SENTINAL, "Event End Time is required"
            end_time = datetime.time.fromisoformat(end_time_raw)
            if end_time <= field:
                return INVALID_SENTINAL, "Event Start Time must be before Event End Time"
            else:
                return next_stage(field, msg)
        except Exception:
            return INVALID_SENTINAL, ""

    return _


def _assert_after_start_time(next_stage: TransformFunc) -> TransformFunc:
    def _(field: Any, msg: RawData) -> Any:
        try:
            start_time = datetime.time.fromisoformat(msg["event_start_time"])
            if start_time >= field:
                return INVALID_SENTINAL, "Event End Time must be after Event Start Time"
            else:
                return next_stage(field, msg)
        except Exception:
            return INVALID_SENTINAL, ""

    return _


def _required_if_has_venue(next_stage: TransformFunc):
    def _(f, msg):
        val = msg.get("event_venue_id")
        return val is not None and val != "" and int(val) != 0

    return required_if(_, next_stage)


CreateEvent = TransformTable(
    "event",
    sanitize={
        "event_title": required(noop),
        "event_venue_id": optional(coerce_pk(transform)),
        "event_recurring_id": optional(coerce_pk(transform)),
        "event_description": required(noop),
        "event_external_link": optional(coerce_str(assert_https(transform))),
        "event_date": required(str_to_date(assert_future_date(transform))),
        "event_start_time": required(str_to_time(_assert_before_end_time(transform))),
        "event_end_time": required(str_to_time(_assert_after_start_time(transform))),
        "event_location_details": _required_if_has_venue(coerce_str(transform)),
        "event_is_av_capable": _required_if_has_venue(coerce_bool(transform)),
    },
    prepare={
        "event_title": noop,
        "event_venue_id": fallback("0", coerce_str(transform)),
        "event_description": noop,
        "event_external_link": fallback("", noop),
        "event_date": date_to_str(transform),
        "event_start_time": time_to_str(transform),
        "event_end_time": time_to_str(transform),
        "event_location_details": fallback("", noop),
        "event_is_av_capable": fallback(False, coerce_bool(transform)),
    },
)


UpdateEvent = TransformTable(
    "event",
    sanitize={
        "event_title": required(noop),
        "event_description": required(noop),
        "event_external_link": optional(coerce_str(assert_https(transform))),
        "event_date": required(str_to_date(assert_future_date(transform))),
        "event_start_time": required(str_to_time(_assert_before_end_time(transform))),
        "event_end_time": required(str_to_time(_assert_after_start_time(transform))),
        "event_venue_id": optional(coerce_pk(transform)),
        "event_location_details": _required_if_has_venue(coerce_str(transform)),
        "event_is_av_capable": _required_if_has_venue(coerce_bool(transform)),
    },
    prepare={
        "event_title": noop,
        "event_description": noop,
        "event_external_link": fallback("", noop),
        "event_date": date_to_str(transform),
        "event_start_time": time_to_str(transform),
        "event_end_time": time_to_str(transform),
        "event_venue_id": fallback("0", coerce_str(transform)),
        "event_location_details": fallback("", noop),
        "event_is_av_capable": fallback(False, coerce_bool(transform)),
    },
)


_is_recurring = lambda f, msg: msg.get("recurring_id") is not None
_required_if_is_recurring = functools.partial(required_if, _is_recurring)

_has_venue = lambda f, msg: msg.get("venue_id") is not None
_required_if_has_venue = functools.partial(required_if, _has_venue)


ListEvent = TransformTable(
    "event",
    sanitize={
        "event_id": read_field("res_id", required(coerce_pk(transform))),
        "event_title": required(noop),
        "event_venue_id": optional(coerce_pk(transform)),
        "event_recurring_id": optional(coerce_pk(transform)),
        "event_description": required(noop),
        "event_external_link": optional(noop),
        "event_date": required(str_to_date(transform)),
        "event_start_time": required(str_to_time(transform)),
        "event_end_time": required(str_to_time(transform)),
        "event_is_cancelled": required(coerce_bool(transform)),
        "event_location_details": optional(coerce_str(transform)),
        "event_is_av_capable": _required_if_provided("venue_id", coerce_bool(transform)),
        "venue_id": optional(coerce_pk(transform)),
        "venue_name": _required_if_provided("venue_id", noop),
        "venue_city": _required_if_provided("venue_id", noop),
        "venue_state": _required_if_provided("venue_id", coerce_str(max_len(2, transform))),
        "venue_address_line1": _required_if_provided("venue_id", noop),
        "venue_address_line2": optional(noop),
        "venue_address_line3": optional(noop),
        "venue_postal_code": _required_if_provided("venue_id", coerce_str(transform)),
    },
    prepare={
        "res_id": read_field("event_id", coerce_str(transform)),
        "event_title": noop,
        "event_description": noop,
        "event_external_link": fallback("", noop),
        "event_date": date_to_str(transform),
        "event_start_time": time_to_str(transform),
        "event_end_time": time_to_str(transform),
        "event_is_cancelled": fallback("", coerce_bool(transform)),
        "event_start": combine_datetime(
            "event_date", "event_start_time", format_as_datetime(transform)
        ),
        "event_end": combine_datetime(
            "event_date", "event_end_time", format_as_datetime(transform)
        ),
        "event_location_details": fallback("", noop),
        "event_is_av_capable": fallback("", coerce_bool(transform)),
        "venue_id": fallback("", noop),
        "venue_name": fallback("", noop),
        "venue_city": fallback("", noop),
        "venue_state": fallback("", coerce_str(transform)),
        "venue_address_line1": fallback("", noop),
        "venue_address_line2": fallback("", noop),
        "venue_address_line3": fallback("", noop),
        "venue_postal_code": fallback("", coerce_str(transform)),
    },
)

ListMember = TransformTable(
    "member",
    {
        "member_id": read_field("res_id", required(coerce_pk(transform))),
        "member_moniker": required(noop),
        "member_first_name": required(noop),
        "member_last_name": required(noop),
        "member_pronouns": optional(noop),
        "member_permissions": required(coerce_int(transform)),
    },
    prepare={
        "res_id": read_field("member_id", coerce_str(transform)),
        "member_moniker": noop,
        "member_first_name": noop,
        "member_last_name": noop,
        "member_pronouns": fallback("", noop),
        "member_permissions": coerce_int(transform),
        "member_role": read_field(
            "member_permissions", coerce_int(role_name_from_permissions(transform))
        ),
    },
)


ListVenue = TransformTable(
    "venue",
    sanitize={
        "venue_id": read_field("res_id", required(coerce_pk(transform))),
        "venue_name": required(noop),
        "venue_city": required(noop),
        "venue_state": required(noop),
        "venue_postal_code": required(coerce_str(transform)),
        "venue_address_line1": required(noop),
        "venue_address_line2": optional(noop),
        "venue_address_line3": optional(noop),
        "venue_external_link": required(coerce_str(assert_https(transform))),
    },
    prepare={
        "res_id": read_field("venue_id", coerce_str(transform)),
        "venue_name": noop,
        "venue_city": noop,
        "venue_state": noop,
        "venue_postal_code": noop,
        "venue_address_line1": noop,
        "venue_address_line2": fallback("", noop),
        "venue_address_line3": fallback("", noop),
        "venue_external_link": noop,
    },
)

ListRecurring = TransformTable(
    "recurring",
    sanitize={
        "recurring_id": read_field("res_id", required(coerce_pk(transform))),
        "recurring_title": noop,
        "recurring_description": required(coerce_str(transform)),
        "recurring_interval_type": required(coerce_pk(transform)),
        "recurring_month": optional(coerce_pk(transform)),
        "recurring_week": optional(coerce_pk(transform)),
        "recurring_day": optional(coerce_pk(transform)),
        "recurring_start_time": required(str_to_time(transform)),
        "recurring_end_time": required(str_to_time(transform)),
    },
    prepare={
        "res_id": read_field("recurring_id", coerce_pk(transform)),
        "recurring_title": noop,
        "recurring_description": noop,
        "recurring_interval_type": fallback(0, coerce_int(transform)),
        "recurring_month": fallback(0, coerce_int(transform)),
        "recurring_week": fallback(0, coerce_int(transform)),
        "recurring_day": fallback(0, coerce_int(transform)),
        "recurring_start_time": time_to_str(transform),
        "recurring_end_time": time_to_str(transform),
        "recurring_interval_summary": read_field(
            "recurring_interval_type", parse_interval_summary(transform)
        ),
        "recurring_next_scheduled_date": compute_next_scheduled_date(format_as_date(transform)),
    },
)
