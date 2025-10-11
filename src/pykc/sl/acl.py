import grammdb

from pykc.constants import MemberRoles
from pykc.dl import (
    crud,
    db,
)
from pykc.sl import structs
from pykc.sl.structs import MemberStruct
from pykc.types import PK


async def grant_member_permission(member_id: PK, permission_bit: MemberRoles) -> MemberRoles:
    async with grammdb.connection_ctx(db.members()) as tr:
        res = await crud.grant_member_permission(tr, member_id, permission_bit)
        await grammdb.commit_transaction(tr)
        return res


async def revoke_member_permission(member_id: PK, permission_bit: MemberRoles) -> MemberRoles:
    async with grammdb.connection_ctx(db.members()) as tr:
        res = await crud.revoke_member_permission(tr, member_id, permission_bit)
        await grammdb.commit_transaction(tr)
        return res


async def set_member_role(member_id: PK, role_bit: MemberRoles) -> MemberRoles:
    async with grammdb.connection_ctx(db.members()) as tr:
        await crud.update_member(tr, id=member_id, permissions=role_bit)
        res = await crud.get_member_permissions(tr, member_id)
        await grammdb.commit_transaction(tr)
        return res


async def update_member(member_id: PK, **new_values) -> MemberStruct:
    async with grammdb.connection_ctx(db.members()) as tr:
        await crud.update_member(tr, id=member_id, **structs.member_raw(new_values))
        res = await crud.get_member_by_id(tr, member_id)
        await grammdb.commit_transaction(tr)
        return structs.member_struct(res)


async def delete_member(member_id: PK) -> PK:
    async with grammdb.connection_ctx(db.members()) as tr:
        res = await crud.delete_member(tr, member_id)
        await grammdb.commit_transaction(tr)
        return res


async def create_member(**values) -> PK:
    async with grammdb.connection_ctx(db.members()) as tr:
        res = await crud.create_member(tr, **structs.member_raw(values))
        await grammdb.commit_transaction(tr)
        return res
