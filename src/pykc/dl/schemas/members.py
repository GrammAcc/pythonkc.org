__all__ = [
    "ApiToken",
    "Member",
    "get_metadata",
]

import sqlalchemy as sa

from .common import (
    columns,
    constraints,
)

_metadata: sa.MetaData = sa.MetaData()


def get_metadata() -> sa.MetaData:
    return _metadata


Member = sa.Table(
    "member",
    _metadata,
    *columns.primary_key(),
    sa.Column("permissions", sa.Integer, default=0),
    sa.Column(
        "moniker",
        sa.Text(collation="NOCASE"),
        constraints.text_nonempty("moniker"),
        constraints.text_no_null_repr("moniker"),
        unique=True,
        nullable=False,
    ),
    sa.Column(
        "first_name",
        sa.Text(collation="NOCASE"),
        constraints.text_no_null_repr("first_name"),
        nullable=False,
        default="",
    ),
    sa.Column(
        "last_name",
        sa.Text(collation="NOCASE"),
        constraints.text_no_null_repr("last_name"),
        nullable=False,
        default="",
    ),
    sa.Column(
        "pronouns",
        sa.Text(collation="NOCASE"),
        constraints.text_no_null_repr("pronouns"),
        nullable=False,
        default="",
    ),
    sa.Column(
        "discord_id",
        sa.Text,
        constraints.text_nonempty("discord_id"),
        constraints.text_no_null_repr("discord_id"),
        unique=True,
        nullable=False,
    ),
    sa.Index("moniker_permissions_idx", "moniker", "permissions"),
    constraints.timestamps_consistency(),
    sqlite_with_rowid=True,
)

ApiToken = sa.Table(
    "api_token",
    _metadata,
    *columns.primary_key(),
    sa.Column(
        "hash",
        sa.Text,
        constraints.text_nonempty("hash"),
        constraints.text_no_null_repr("hash"),
        nullable=False,
        unique=True,
    ),
    sa.Column(
        "jwt",
        sa.Text,
        constraints.text_nonempty("jwt"),
        constraints.text_no_null_repr("jwt"),
        nullable=False,
        unique=True,
    ),
    sa.Column("revoked", sa.Boolean, default=False),
    constraints.timestamps_consistency(),
    sqlite_with_rowid=True,
)
