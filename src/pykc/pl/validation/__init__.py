__all__ = [
    "changeset",
    "constants",
    "contracts",
    "prepare",
    "sanitize",
    "validations",
    "transforms",
]


from pykc.sl.structs import STRUCT
from pykc.types import RawData

from . import (
    constants,
    contracts,
    transforms,
    validations,
)


def sanitize(dispatch_table: contracts.TransformTable, msg: RawData) -> contracts.SanitizeResult:
    result = {
        k: dispatch_table.sanitize[k](msg.get(k), msg) for k in dispatch_table.sanitize.keys()
    }
    missing_errors = [
        (k, "required") for k, v in result.items() if v[0] is constants.REQUIRED_SENTINAL
    ]
    invalid_errors = [
        (k, v[1] if v[1] != "" else "invalid")
        for k, v in result.items()
        if v[0] is constants.INVALID_SENTINAL
    ]
    errors = [*missing_errors, *invalid_errors]
    filtered = {k: v[0] for k, v in result.items() if v[0] is not constants.OPTIONAL_SENTINAL}
    if len(errors) > 0:
        return contracts.SanitizeResult(success=False, errors=errors, data=filtered)
    else:
        return contracts.SanitizeResult(success=True, errors=[], data=filtered)


def prepare(dispatch_table: contracts.TransformTable, msg: STRUCT | RawData) -> RawData:
    """Prepare a data structure for JSON serialization.

    Generally, this can be thought of as the reverse of the `sanitize` function for a particular
    workflow.

    In other words, the data returned by the `sanitize` function is suitable as input for the second
    argument of the `prepare` function, and the output of the `prepare` function is suitable as the
    second argument of the `sanitize` function.

    """

    return {k: dispatch_table.prepare[k](msg.get(k), msg)[0] for k in dispatch_table.prepare.keys()}


def changeset(
    dispatch_table: contracts.TransformTable, modified: RawData, stored: STRUCT
) -> contracts.Changeset:
    """Prepare a changeset result.

    The `Changeset` data structure can be used to build a message for live feedback over websockets
    about the state of a form the user is editing or for any other uses such as determining if a
    DOM element needs to be updated due to the displayed data having been changed by another
    user/task.
    """

    modified_sanitized = sanitize(dispatch_table, modified)
    modified_prepared = prepare(dispatch_table, modified_sanitized.data)
    stored_prepared = prepare(dispatch_table, stored)

    changes = {k: (v != stored_prepared[k]) for k, v in modified_prepared.items()}
    changed = [k for k, v in changes.items() if v]
    unchanged = [k for k, v in changes.items() if not v]
    return contracts.Changeset(changed=changed, unchanged=unchanged)
