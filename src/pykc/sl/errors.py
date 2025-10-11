import enum
from collections.abc import Coroutine
from typing import (
    Any,
    Literal,
)

from grammdb.exceptions import (
    ConstraintError,
    constraint_error,
)
from sqlalchemy.exc import (
    MultipleResultsFound,
    NoResultFound,
)

from pykc.common import logs
from pykc.exceptions import (
    DataError,
    IntegrityError,
    MultiplicityError,
)


class Err(enum.IntFlag):
    """Enum representing errors as values for use in structural pattern matching."""

    OK = 0  # Indicates operation succeeded without errors.
    FAILED = enum.auto()  # Indicates operation failed but not any specific error.
    WTF = enum.auto()  # unknown error.
    # Domain-specific errors.
    INTEGRITY = enum.auto()
    QUANTITY = enum.auto()
    INVALID = enum.auto()
    AUTH = enum.auto()


type ErrorTuple[T] = tuple[Literal[Err.OK], T] | tuple[Literal[Err.FAILED], Err]
"""A generic result type that wraps error values for structural pattern matching.

The first element of the tuple is either `Err.OK` indicating the operation succeeded or
`Err.FAILED` indicating the operation failed.

The second element of the tuple is either the result of the successful operation, or the
domain-specific error value that can be matched against for different error handling paths.

Example:
    >>> from pathlib import Path
    >>> def load_from_files(fp) -> ErrorTuple[list[str] | str]:
    ...     try:
    ...         if (p := Path(fp)).exists():
    ...             if p.is_dir():
    ...                 return Err.OK, [f.read_text() for f in p.iterdir() if f.is_file()]
    ...             elif p.is_file():
    ...                 return Err.OK, p.read_text()
    ...             else:
    ...                 # Not a directory or a file.
    ...                 return Err.FAILED, Err.WTF
    ...         else:
    ...             return Err.FAILED, Err.INVALID
    ...     except OSError:
    ...         return Err.FAILED, Err.INVALID
    ...     except Exception:
    ...         return Err.FAILED, Err.WTF
    >>> def load_data() -> str:
    ...     match load_from_files("badpath"):
    ...         case Err.OK, str(val):
    ...             return val
    ...         case Err.OK, list(val):
    ...             return ",".join(val)
    ...         case Err.FAILED, err:
    ...             return "could not load data"
    >>> load_data()
    'could not load data'
"""


async def return_if_err[R](coro: Coroutine[Any, Any, R]) -> ErrorTuple[R]:
    """Log exceptions and return a structured error tuple that can be used in pattern matching."""

    try:
        with constraint_error():
            res = await coro
            return Err.OK, res
    except ConstraintError as e:
        await logs.log_constraint_error(e, caller=coro)
        return Err.FAILED, Err.INTEGRITY
    except (NoResultFound, MultipleResultsFound) as e:
        await logs.log_unique_result_error(e, caller=coro)
        return Err.FAILED, Err.QUANTITY
    except Exception as e:
        await logs.log_unknown_error(e, caller=coro)
        return Err.FAILED, Err.WTF


async def raise_if_err[R](coro: Coroutine[Any, Any, R]) -> R:
    """Log internal exceptions and raise domain-specific exceptions."""
    try:
        with constraint_error():
            res = await coro
            return res
    except ConstraintError as e:
        await logs.log_constraint_error(e, caller=coro)
        raise IntegrityError
    except (NoResultFound, MultipleResultsFound) as e:
        await logs.log_unique_result_error(e, caller=coro)
        raise MultiplicityError
    except Exception as e:
        await logs.log_unknown_error(e, caller=coro)
        raise DataError
