import os
from test import mock_data

import grammdb

from pykc.common import appenv
from pykc.dl import (
    crud,
    db,
)

appenv.load()


async def members():
    await db.init(db.members(), os.environ["MEMBERS_DB_URI"], drop_tables=True)
    tr = await grammdb.start_transaction(db.members())
    seed_data = mock_data.resources()["seed"]
    for member_data in seed_data["Member"]:
        await crud.create_member(tr, **member_data)
    for token_data in seed_data["ApiToken"]:
        await crud.create_token(tr, **token_data)
    await grammdb.commit_transaction(tr)


async def events():
    await db.init(db.events(), os.environ["EVENTS_DB_URI"], drop_tables=True)
    tr = await grammdb.start_transaction(db.events())
    seed_data = mock_data.resources()["seed"]
    for recurring_data in seed_data["Recurring"]:
        await crud.create_recurring(tr, **recurring_data)
    for venue_data in seed_data["Venue"]:
        await crud.create_venue(tr, **venue_data)
    for event_data in seed_data["Event"]:
        await crud.create_event(tr, **event_data)
    await grammdb.commit_transaction(tr)
