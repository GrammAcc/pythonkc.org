import sqlalchemy as sa

from pykc.dl import tables

_all_members_columns = [
    *tables.COLUMN_NAMES["members"],
    *tables.COLUMN_ALIASES["api_tokens"],
]

_all_events_columns = [
    *tables.COLUMN_NAMES["events"],
    *[i for i in tables.COLUMN_ALIASES["recurring"] if i.name != "recurring_id"],
    *[i for i in tables.COLUMN_ALIASES["venues"] if i.name != "venue_id"],
]


def members() -> sa.Select:
    return sa.select(*tables.COLUMN_NAMES["members"])


def tokens() -> sa.Select:
    return sa.select(*tables.COLUMN_NAMES["api_tokens"])


def events() -> sa.Select:
    base_join = sa.outerjoin(
        tables.Event,
        tables.Recurring,
        tables.Event.c.recurring_id == tables.Recurring.c.id,
    )
    final_join = base_join.outerjoin(tables.Venue, tables.Event.c.venue_id == tables.Venue.c.id)

    return sa.select(*_all_events_columns).select_from(final_join)


def recurring() -> sa.Select:
    return sa.select(*tables.COLUMN_NAMES["recurring"])


def venues() -> sa.Select:
    return sa.select(*tables.COLUMN_NAMES["venues"])
