import asyncio
import os

import grammdb

from pykc.common import appenv
from pykc.constants import MemberRoles
from pykc.dl import (
    crud,
    db,
)
from pykc.sl import tokens

appenv.load()


async def run():
    await db.init(db.members(), os.environ["MEMBERS_DB_URI"], drop_tables=True, echo=True)
    if os.environ["APPENV"] == "dev":
        tr = await grammdb.start_transaction(db.members())
        members = [
            {
                "moniker": "Moderator",
                "first_name": "Johnny",
                "last_name": "Test",
                "pronouns": "he/him",
                "permissions": MemberRoles.MODERATOR,
                "password_hash": tokens.pw_hasher().hash("TestLogin"),
            },
            {
                "moniker": "Developer",
                "first_name": "Susan",
                "last_name": "Test",
                "pronouns": "she/her",
                "permissions": MemberRoles.DEVELOPER,
                "password_hash": tokens.pw_hasher().hash("TestLogin"),
            },
            {
                "moniker": "Event Manager",
                "first_name": "Mary",
                "last_name": "Test",
                "pronouns": "she/her",
                "permissions": MemberRoles.EVENT_MANAGER,
                "password_hash": tokens.pw_hasher().hash("TestLogin"),
            },
            {
                "moniker": "Organizer",
                "first_name": "Lila",
                "last_name": "Test",
                "pronouns": "she/her",
                "permissions": MemberRoles.ORGANIZER,
                "password_hash": tokens.pw_hasher().hash("TestLogin"),
            },
        ]
        for member in members:
            await crud.create_member(tr, **member)
        await grammdb.commit_transaction(tr)


asyncio.run(run())
