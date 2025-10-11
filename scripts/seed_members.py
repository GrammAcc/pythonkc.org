import asyncio
import os

from pykc.common import appenv
from pykc.dl import db

appenv.load()


async def run():
    await db.init(db.members(), os.environ["MEMBERS_DB_URI"], drop_tables=True, echo=True)


asyncio.run(run())
