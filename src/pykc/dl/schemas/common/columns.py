import sqlalchemy as sa

from pykc.types import PK


def primary_key() -> tuple[sa.Column[PK]]:
    """This helper function makes refactoring easier if we need to change
    primary key types."""

    return (sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),)
