from typing import (
    Any,
    NamedTuple,
    Protocol,
)

from pykc.types import RawData


class TransformFunc(Protocol):
    def __call__(self, field: Any, msg: RawData) -> tuple[Any, str]: ...


class TransformSegment(Protocol):
    def __call__(self, field: Any, msg: RawData) -> Any: ...


class ConditionFunc(Protocol):
    def __call__(self, field: Any, msg: RawData) -> tuple[bool, TransformFunc]: ...


class Changeset(NamedTuple):
    changed: list[str]
    unchanged: list[str]


class SanitizeResult(NamedTuple):
    success: bool
    errors: list[tuple[str, str]]
    data: RawData


class TransformTable(NamedTuple):
    resource: str
    sanitize: dict[str, TransformFunc]
    prepare: dict[str, TransformFunc]
