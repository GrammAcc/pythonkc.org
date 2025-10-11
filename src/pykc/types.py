from typing import Any

type PK = int
"""Update this to match the datatype of the primary keys used in the sqlalchemy schemas
if we change them."""

type RawData = dict[str, Any]
