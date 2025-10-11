import sqlalchemy as sa

from pykc.dl import tables

_all_members_columns = [
    *tables.COLUMN_ALIASES["members"],
    *tables.COLUMN_ALIASES["api_tokens"],
]

_all_events_columns = [
    *tables.COLUMN_ALIASES["events"],
    *tables.COLUMN_ALIASES["recurring"],
    *tables.COLUMN_ALIASES["venues"],
]


def members() -> sa.Select:
    return sa.select(*tables.COLUMN_ALIASES["members"])


def tokens() -> sa.Select:
    return sa.select(*tables.COLUMN_ALIASES["api_tokens"])


def events() -> sa.Select:
    base_join = sa.outerjoin(
        tables.Event,
        tables.Recurring,
        tables.Event.c.recurring_id == tables.Recurring.c.id,
    )
    final_join = base_join.outerjoin(tables.Venue, tables.Event.c.venue_id == tables.Venue.c.id)

    return sa.select(*_all_events_columns).select_from(final_join)


def recurring() -> sa.Select:
    return sa.select(*tables.COLUMN_ALIASES["recurring"])


def venues() -> sa.Select:
    return sa.select(*tables.COLUMN_ALIASES["venues"])
