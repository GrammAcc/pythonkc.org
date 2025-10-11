import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine


def enable_sqlite_fks(engine: AsyncEngine) -> None:
    def _(async_con, dbapi_con, connection_record=None):
        async_con.cursor().execute("PRAGMA foreign_keys = ON;")

    sa.event.listen(engine.sync_engine, "connect", _)
