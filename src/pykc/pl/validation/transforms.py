import datetime
import functools
from collections.abc import Callable
from typing import Any

import grammlog

from pykc.common import logs
from pykc.constants import (
    DATE_FORMAT,
    DATETIME_FORMAT,
    TIME_FORMAT,
    TIMEZONE,
    EventIntervalType,
    MemberRoles,
)
from pykc.sl import scheduling
from pykc.types import RawData

from .constants import INVALID_SENTINAL
from .contracts import (
    TransformFunc,
    TransformSegment,
)


def noop(field: Any, msg: dict[str, Any]) -> tuple[Any, str]:
    return field, ""


def transform(field: Any, msg: dict[str, Any]) -> tuple[Any, str]:
    return field, ""


def validation_error(
    err_msg: str, next_stage: TransformFunc
) -> Callable[[TransformSegment], TransformFunc]:
    def outer(func):
        @functools.wraps(func)
        def inner(field: str, msg: RawData) -> tuple[Any, str]:
            try:
                transformed = func(field, msg)
            except Exception as e:
                logs.log_validation_error(e, caller=func)
                return INVALID_SENTINAL, err_msg
            else:
                return next_stage(transformed, msg)

        return inner

    return outer


def str_to_datetime(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("invalid datetime string", next_stage)
    def _(field: str, msg: dict[str, Any]) -> datetime.datetime:
        return datetime.datetime.fromisoformat(field)

    return _


def str_to_date(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("invalid date string", next_stage)
    def _(field: str, msg: dict[str, Any]) -> datetime.date:
        return datetime.date.fromisoformat(field)

    return _


def str_to_time(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("invalid time string", next_stage)
    def _(field: str, msg: dict[str, Any]) -> datetime.time:
        return datetime.time.fromisoformat(field)

    return _


def datetime_to_str(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: datetime.datetime, msg: dict[str, Any]) -> str:
        return field.isoformat()

    return _


def date_to_str(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: datetime.date, msg: dict[str, Any]) -> str:
        return field.isoformat()

    return _


def time_to_str(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: datetime.time, msg: dict[str, Any]) -> str:
        return field.isoformat()

    return _


def checkbox_to_bool(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: Any, msg: RawData) -> bool:
        return str(field) == "on"

    return _


def coerce_bool(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: Any, msg: dict[str, Any]) -> bool:
        if field == "false":
            return False
        else:
            return bool(field)

    return _


def uppercase(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: str, msg: RawData) -> str:
        return field.upper()

    return _


def coerce_str(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: Any, msg: dict[str, Any]) -> str:
        return str(field)

    return _


def coerce_pk(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: Any, msg: dict[str, Any]) -> int | None:
        transformed = int(field)
        if transformed == 0:
            # 0 is a sentinal value the FE sends to indicate we should
            # remove an FK field from a resource, so we set to None.
            return None
        else:
            return transformed

    return _


def coerce_int(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: Any, msg: dict[str, Any]) -> int:
        return int(field)

    return _


def coerce_float(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: Any, msg: dict[str, Any]) -> float:
        return float(field)

    return _


def read_field(override_field_name: str, next_stage: TransformFunc) -> TransformFunc:
    def _(field: Any, msg: dict[str, Any]) -> tuple[Any, str]:
        return next_stage(msg.get(override_field_name), msg)

    return _


def read_first_field(field_names: list[str], next_stage: TransformFunc) -> TransformFunc:
    def _(field: Any, msg: dict[str, Any]) -> tuple[Any, str]:
        override_field = None
        for field_name in field_names:
            if (found_field := msg.get(field_name, None)) is not None:
                override_field = found_field
                break

        return next_stage(override_field, msg)

    return _


def datetime_to_time(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: datetime.datetime, msg: dict[str, Any]) -> datetime.time:
        return field.time()

    return _


def datetime_to_date(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: datetime.datetime, msg: dict[str, Any]) -> datetime.date:
        return field.date()

    return _


def combine_datetime(
    date_transform: TransformFunc, time_transform: TransformFunc, next_stage: TransformFunc
) -> TransformFunc:
    def _(field: Any, msg: dict[str, Any]) -> tuple[Any, str]:
        try:
            date_val, _ = date_transform(field, msg)
            time_val, _ = time_transform(field, msg)

            transformed = datetime.datetime.combine(date_val, time_val)
        except Exception as e:
            grammlog.error(logs.err_log, "validation failed", err=e)
            return INVALID_SENTINAL, ""
        else:
            return next_stage(transformed, msg)

    return _


def format_as_date(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: datetime.date | datetime.datetime, msg: dict[str, Any]) -> str:
        return field.strftime(DATE_FORMAT)

    return _


def format_as_datetime(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: datetime.date | datetime.datetime, msg: dict[str, Any]) -> str:
        if isinstance(field, datetime.datetime):
            return field.astimezone(TIMEZONE).strftime(DATETIME_FORMAT)
        else:
            return field.strftime(DATETIME_FORMAT)

    return _


def role_name_from_permissions(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: int, msg: dict[str, Any]) -> str:
        match field:
            case MemberRoles.ORGANIZER:
                return "Organizer"
            case MemberRoles.EVENT_MANAGER:
                return "Event Manager"
            case MemberRoles.DEVELOPER:
                return "Developer"
            case MemberRoles.MODERATOR:
                return "Moderator"
            case _:
                return "Member"

    return _


def compute_next_scheduled_date(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: Any, msg: RawData) -> datetime.date | object:
        return scheduling.compute_next_event_date(msg, datetime.date.today())

    return _


def parse_interval_summary(next_stage: TransformFunc) -> TransformFunc:
    @validation_error("", next_stage)
    def _(field: Any, msg: dict[str, Any]) -> str | object:
        weekdays = {
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
            7: "Sunday",
        }

        weeks = {
            1: "first",
            2: "second",
            3: "third",
            4: "fourth",
        }

        months = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }

        start_time = msg["recurring_start_time"].strftime(TIME_FORMAT)
        end_time = msg["recurring_end_time"].strftime(TIME_FORMAT)
        time_slot = f"from {start_time} to {end_time}"

        match field:
            case EventIntervalType.DAILY:
                return f"Every day {time_slot}"
            case EventIntervalType.WEEKLY:
                day = weekdays[msg["recurring_day"]]
                return f"Every {day} {time_slot}"
            case EventIntervalType.MONTHLY:
                day = weekdays[msg["recurring_day"]]
                week = weeks[msg["recurring_week"]]
                return f"Every {week} {day} of the month {time_slot}"
            case EventIntervalType.QUARTERLY:
                day = weekdays[msg["recurring_day"]]
                week = weeks[msg["recurring_week"]]
                return f"Every quarter on the {week} {day} of the month {time_slot}"
            case EventIntervalType.SEMIYEARLY:
                day = weekdays[msg["recurring_day"]]
                week = weeks[msg["recurring_week"]]
                return f"Every six months on the {week} {day} of the month {time_slot}"
            case EventIntervalType.YEARLY:
                day = weekdays[msg["recurring_day"]]
                week = weeks[msg["recurring_week"]]
                month = months[msg["recurring_month"]]
                return f"Every {week} {day} of {month} each year {time_slot}"
            case _:
                raise ValueError(f"invalid interval type: {field}")

    return _
