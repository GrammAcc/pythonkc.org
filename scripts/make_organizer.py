import asyncio
import os
import sys

from pykc.common import appenv
from pykc.constants import MemberRoles
from pykc.dl import db
from pykc.sl import (
    acl,
    fetch,
)

appenv.load()


async def run():
    moniker = sys.argv[1]
    await db.init(db.members(), os.environ["MEMBERS_DB_URI"], drop_tables=False, echo=True)
    member = await fetch.member_by_moniker(moniker)
    await acl.set_member_role(member["member_id"], MemberRoles.ORGANIZER)


asyncio.run(run())
