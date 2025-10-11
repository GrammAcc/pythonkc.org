from collections.abc import (
    Callable,
    Coroutine,
)

import grammlog
from grammdb.exceptions import ConstraintError
from sqlalchemy.exc import (
    MultipleResultsFound,
    NoResultFound,
)

err_log = grammlog.make_logger("error")


async def log_unknown_error(err: Exception, caller: Callable | Coroutine):
    await grammlog.async_debug(
        err_log,
        "unknown error",
        {"domain": "unhandled_error", "caller": caller.__qualname__},
        err=err,
    )


async def log_unique_result_error(
    err: NoResultFound | MultipleResultsFound, caller: Callable | Coroutine, **data
) -> None:
    await grammlog.async_debug(
        err_log,
        "Expected unique result.",
        {"domain": "database", "caller": caller.__qualname__, **data},
        err=err,
    )


async def log_constraint_error(err: ConstraintError, caller: Callable | Coroutine, **data) -> None:
    await grammlog.async_debug(
        err_log,
        "constraint violation.",
        {"domain": "database", "caller": caller.__qualname__, **data},
        err=err,
    )


def log_validation_error(err: Exception, caller: Callable | Coroutine):
    # Use the named validation function and not the inner TransformFunc for the caller.
    path_parts = caller.__qualname__.split(".")
    locals_idx = path_parts.index("<locals>")
    caller_path = ".".join(path_parts[:locals_idx])

    grammlog.debug(
        err_log,
        "validation failed",
        {"domain": "input_validation", "caller": caller_path},
        err=err,
    )


async def log_oauth_error(msg: str, caller: Callable | Coroutine, **data) -> None:
    await grammlog.async_debug(
        err_log,
        "oauth login failed",
        {"domain": "auth", "caller": caller.__qualname__, "extra_msg": msg, **data},
        err=data.get("err", None),
    )
