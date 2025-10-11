__all__ = [
    "Event",
    "Recurring",
    "Venue",
    "get_metadata",
]

import sqlalchemy as sa

from pykc.constants import EventIntervalType

from .common import (
    columns,
    constraints,
)

_metadata: sa.MetaData = sa.MetaData()


def get_metadata() -> sa.MetaData:
    return _metadata


Event = sa.Table(
    "event",
    _metadata,
    *columns.primary_key(),
    sa.Column(
        "title",
        sa.String(64),
        constraints.text_nonempty("title"),
        constraints.text_no_null_repr("title"),
        nullable=False,
    ),
    sa.Column(
        "description",
        sa.Text,
        constraints.text_nonempty("description"),
        constraints.text_no_null_repr("description"),
        nullable=False,
    ),
    sa.Column(
        "start",
        sa.DateTime(),
        nullable=False,
    ),
    sa.Column(
        "end",
        sa.DateTime(),
        nullable=False,
    ),
    sa.Column(
        "external_link",
        sa.Text,
        constraints.url_is_https("external_link"),
        unique=True,
        nullable=True,
    ),
    sa.Column(
        "recurring_id",
        sa.Integer,
        sa.ForeignKey("recurring.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    ),
    sa.Column(
        "is_cancelled",
        sa.Boolean,
        nullable=False,
        default=False,
    ),
    sa.Column(
        "venue_id",
        sa.Integer,
        sa.ForeignKey("venue.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    ),
    sa.Column(
        "location_details",
        sa.String(64),
        constraints.text_nonempty("location_details"),
        constraints.text_no_null_repr("location_details"),
        nullable=True,
    ),
    sa.Column("is_av_capable", sa.Boolean, nullable=False, default=False),
    constraints.relative_time("start", "end"),
    constraints.timestamps_consistency(),
    sa.Index("event_start_end_idx", "start", "end"),
    sqlite_with_rowid=True,
)

Recurring = sa.Table(
    "recurring",
    _metadata,
    *columns.primary_key(),
    sa.Column(
        "title",
        sa.String(64),
        constraints.text_nonempty("title"),
        constraints.text_no_null_repr("title"),
        nullable=False,
        unique=True,
    ),
    sa.Column(
        "description",
        sa.Text,
        constraints.text_nonempty("description"),
        constraints.text_no_null_repr("description"),
        nullable=False,
    ),
    sa.Column(
        "interval_type",
        sa.Integer,
        constraints.enum_member("interval_type", EventIntervalType),
        nullable=False,
    ),
    sa.Column(
        "month",
        sa.Integer,
        constraints.integer_range("month", 0, 13),
        sa.CheckConstraint(
            f"(month IS NOT NULL) OR (interval_type <> {EventIntervalType.YEARLY.value})",
            name="month_required_if_yearly_interval",
        ),
        nullable=True,
    ),
    sa.Column(
        "week",
        sa.Integer,
        constraints.integer_range("week", 0, 5),
        sa.CheckConstraint(
            f"(week IS NOT NULL) \
OR (interval_type = {EventIntervalType.DAILY.value}) \
OR (interval_type = {EventIntervalType.WEEKLY.value})",
            name="week_required_if_not_daily_or_weekly_interval",
        ),
        nullable=True,
    ),
    sa.Column(
        "day",
        sa.Integer,
        constraints.integer_range("day", 0, 8),
        sa.CheckConstraint(
            f"(day IS NOT NULL) OR (interval_type = {EventIntervalType.DAILY.value})",
            name="day_required_if_not_daily_interval",
        ),
        nullable=True,
    ),
    sa.Column(
        "start_time",
        sa.Time(),
        nullable=False,
    ),
    sa.Column(
        "end_time",
        sa.Time(),
        nullable=False,
    ),
    constraints.relative_time("start_time", "end_time"),
    constraints.timestamps_consistency(),
    sqlite_with_rowid=True,
)

Venue = sa.Table(
    "venue",
    _metadata,
    *columns.primary_key(),
    sa.Column(
        "name",
        sa.String(64),
        constraints.text_nonempty("name"),
        constraints.text_no_null_repr("name"),
        unique=True,
        nullable=False,
    ),
    sa.Column(
        "city",
        sa.String(32),
        constraints.text_nonempty("city"),
        constraints.text_no_null_repr("city"),
        nullable=False,
    ),
    sa.Column(
        "state",
        sa.String(2),
        constraints.text_nonempty("state"),
        constraints.text_no_null_repr("state"),
        nullable=False,
    ),
    sa.Column(
        "postal_code",
        sa.String(10),
        constraints.text_nonempty("postal_code"),
        constraints.text_no_null_repr("postal_code"),
        nullable=False,
    ),
    sa.Column(
        "address_line1",
        sa.String(64),
        constraints.text_nonempty("address_line1"),
        constraints.text_no_null_repr("address_line1"),
        nullable=False,
    ),
    sa.Column(
        "address_line2",
        sa.String(64),
        constraints.text_nonempty("address_line2"),
        constraints.text_no_null_repr("address_line2"),
        nullable=True,
    ),
    sa.Column(
        "address_line3",
        sa.String(64),
        constraints.text_nonempty("address_line3"),
        constraints.text_no_null_repr("address_line3"),
        nullable=True,
    ),
    sa.Column(
        "external_link",
        sa.Text,
        constraints.url_is_https("external_link"),
        unique=False,
        nullable=False,
    ),
    constraints.timestamps_consistency(),
    sqlite_with_rowid=True,
)
