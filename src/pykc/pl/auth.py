import functools

from quart import g
from quart import session as quart_session

from pykc.pl import res_helpers
from pykc.types import PK


def has_permission(permission_bit: int) -> bool:
    member_permissions = g.get("member_permissions", 0)
    return bool(permission_bit & member_permissions)


def requires_permission(permission_bit: int):
    def outer(func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            if has_permission(permission_bit):
                return await func(*args, **kwargs)
            else:
                return res_helpers.forbidden()

        return inner

    return outer


def get_logged_in_member_id_or_none() -> PK | None:
    if "member_id" in quart_session:
        return quart_session["member_id"]
    elif "member_id" in g:
        return g.get("member_id")
    else:
        return None


def get_logged_in_member_id() -> PK:
    member_id = get_logged_in_member_id_or_none()
    assert member_id is not None
    return member_id


def member_matches_session_user(member_id: PK) -> bool:
    return get_logged_in_member_id() == member_id
