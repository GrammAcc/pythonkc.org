import sqlalchemy as sa
from grammdb import (
    select,
    update,
)
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncResult,
)

from pykc.constants import MemberRoles
from pykc.dl import (
    from_,
    tables,
    where,
)

from .factories import (
    make_create,
    make_delete,
    make_update,
)


async def get_members(tr: AsyncConnection) -> AsyncResult:
    stmt = select("*", from_.members()).order_by(tables.Member.c.moniker.asc())
    members = await tr.stream(stmt)
    return members


async def search_members(tr: AsyncConnection, search_query: str) -> AsyncResult:
    # TODO: Include first and last name in search.
    stmt = select("*", from_.members(), where.moniker_like(search_query)).order_by(
        tables.Member.c.moniker.asc()
    )
    members = await tr.stream(stmt)
    return members


async def get_member_by_id(tr: AsyncConnection, member_id: int) -> sa.Row:
    stmt = select("*", from_.members(), where.member_id_is(member_id))
    member = await tr.execute(stmt)
    return member.one()


async def get_member_by_moniker(tr: AsyncConnection, moniker: str) -> sa.Row:
    stmt = select("*", from_.members(), where.moniker_is(moniker))
    member = await tr.execute(stmt)
    return member.one()


async def get_member_by_discord_id(tr: AsyncConnection, discord_id: str) -> sa.Row:
    stmt = select("*", from_.members(), where.discord_id_is(discord_id))
    member = await tr.execute(stmt)
    return member.one()


async def get_member_permissions(tr: AsyncConnection, member_id: int) -> MemberRoles:
    stmt = select("member_permissions", from_.members(), where.member_id_is(member_id))
    res = await tr.execute(stmt)
    return res.scalar_one()


async def get_token_by_hash(tr: AsyncConnection, token_hash: str) -> sa.Row:
    stmt = select(
        "*", from_.tokens(), where.token_hash_is(token_hash), where.token_is_not_revoked()
    )
    res = await tr.execute(stmt)
    return res.one()


async def grant_member_permission(
    tr: AsyncConnection, member_id: int, permission_bit: MemberRoles
) -> MemberRoles:
    stmt = update(
        tables.Member,
        where.member_id_is(member_id),
        permissions=tables.Member.c.permissions.op("|")(int(permission_bit)),
    ).returning(tables.Member.c.permissions)
    result = await tr.execute(stmt)
    return result.scalar_one()


async def revoke_member_permission(
    tr: AsyncConnection, member_id: int, permission_bit: MemberRoles
) -> MemberRoles:
    stmt = update(
        tables.Member,
        where.member_id_is(member_id),
        permissions=tables.Member.c.permissions.op("&")(~int(permission_bit)),
    ).returning(tables.Member.c.permissions)
    result = await tr.execute(stmt)
    return result.scalar_one()


create_member = make_create(tables.Member)
create_token = make_create(tables.ApiToken)
update_member = make_update(tables.Member)
update_token = make_update(tables.ApiToken)
delete_member = make_delete(tables.Member)
delete_token = make_delete(tables.ApiToken)
