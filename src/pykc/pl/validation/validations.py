import datetime
from collections.abc import Callable
from typing import Any

import grammlog

from pykc.common import logs
from pykc.types import RawData

from .constants import (
    INVALID_SENTINAL,
    OPTIONAL_SENTINAL,
    REQUIRED_SENTINAL,
)
from .contracts import TransformFunc


def optional(next_stage: TransformFunc) -> TransformFunc:
    """Short-circuit the transform chain if the field is not provided"""

    def _(field: Any | None, msg: dict[str, Any]) -> Any:
        if field is None or field == "":
            return OPTIONAL_SENTINAL, ""
        else:
            return next_stage(field, msg)

    return _


def fallback(fb_value: Any, next_stage: TransformFunc) -> TransformFunc:
    """Short-circuit to `fb_value` instead of removing the field."""

    def _(field: Any | None, msg: dict[str, Any]) -> Any:
        if field is None:
            return fb_value, ""
        else:
            return next_stage(field, msg)

    return _


def required(next_stage: TransformFunc) -> TransformFunc:
    def _(field: Any | None, msg: dict[str, Any]) -> Any:
        if field is None or field == "":
            return REQUIRED_SENTINAL, ""
        else:
            return next_stage(field, msg)

    return _


def required_if(
    cond_func: Callable[[Any, RawData], bool], next_stage: TransformFunc
) -> TransformFunc:
    def _(field: Any, msg: dict[str, Any]) -> Any:
        if field is None or field == "":
            cond = cond_func(field, msg)
            if cond:
                return REQUIRED_SENTINAL, ""
            else:
                return OPTIONAL_SENTINAL, ""
        else:
            return next_stage(field, msg)

    return _


def assert_enum(enum_class: Any, next_stage: TransformFunc) -> TransformFunc:
    def _(field: Any, msg: dict[str, Any]) -> Any:
        if field in enum_class:
            return next_stage(field, msg)
        else:
            grammlog.debug(
                logs.err_log,
                "got non-enum member",
                {
                    "domain": "input_validation",
                    "caller": assert_enum,
                    "field_value": field,
                    "enum_class": enum_class.__name__,
                },
            )
            return INVALID_SENTINAL, f"{field} is not a valid value for {enum_class.__name__}"

    return _


def assert_future_date(next_stage: TransformFunc) -> TransformFunc:
    def _(field: Any, msg: RawData) -> Any:
        if field <= datetime.date.today():
            return INVALID_SENTINAL, "Must be a future date"
        else:
            return next_stage(field, msg)

    return _


def assert_https(next_stage: TransformFunc) -> TransformFunc:
    def _(field: Any, msg: RawData) -> Any:
        if not field.startswith("https://"):
            return INVALID_SENTINAL, "URL must be HTTPS"
        else:
            return next_stage(field, msg)

    return _


def max_len(limit: int, next_stage: TransformFunc) -> TransformFunc:
    def _(field: Any, msg: RawData) -> Any:
        try:
            if len(field) > limit:
                return INVALID_SENTINAL, f"max length is {limit}"
            else:
                return next_stage(field, msg)
        except Exception as e:
            logs.log_validation_error(e, caller=max_len)
            return INVALID_SENTINAL, ""

    return _
