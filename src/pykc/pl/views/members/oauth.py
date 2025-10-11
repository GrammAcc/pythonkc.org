import os

import aiohttp

from pykc.exceptions import ValidationError
from pykc.pl import (
    dtos,
    utils,
    validation,
)
from pykc.sl import (
    acl,
    fetch,
    pubsub,
)
from pykc.types import (
    PK,
    RawData,
)

_CLIENT_SESSION: aiohttp.ClientSession | None = None


def _get_session() -> aiohttp.ClientSession:
    global _CLIENT_SESSION
    if _CLIENT_SESSION is None:
        _CLIENT_SESSION = aiohttp.ClientSession(base_url="https://discord.com/api/v10/")
    return _CLIENT_SESSION


CLIENT_ID = os.environ["DISCORD_CLIENT_ID"]
CLIENT_SECRET = os.environ["DISCORD_CLIENT_SECRET"]
REDIRECT_URI = utils.get_site_root() + "/members/login/discord"


async def _discord_token_request(data):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with _get_session().post(
        "oauth2/token",
        data=data,
        headers=headers,
        auth=aiohttp.BasicAuth(CLIENT_ID, CLIENT_SECRET),
    ) as r:
        return r.status, await r.json()


async def discord_exchange_code(code, state) -> tuple[int, dict]:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "state": state,
        "redirect_uri": REDIRECT_URI,
    }
    return await _discord_token_request(data)


async def discord_refresh_token(refresh_token) -> tuple[int, dict]:
    data = {"grant_type": "refresh_token", "refresh_token": refresh_token}

    return await _discord_token_request(data)


async def discord_get_user_profile(access_token) -> tuple[int, dict]:
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    async with _get_session().get(
        f"users/@me/guilds/{768563824999399464}/member", headers=headers
    ) as r:
        return r.status, await r.json()


async def create_member_from_discord(discord_user_data: RawData) -> PK:
    if not (
        sanitized := validation.sanitize(dtos.CreateMemberFromDiscord, discord_user_data["user"])
    ).success:
        raise ValidationError(sanitized.errors)
    else:
        new_member_pk = await acl.create_member(**sanitized.data)
        new_member = await fetch.member_by_id(new_member_pk)
        prepared = validation.prepare(dtos.CreateMember, new_member)
        msg = {
            "type": pubsub.MsgTypes.LIST_ADD,
            "res_id": new_member_pk,
            "resource": prepared,
        }
        await pubsub.publish(pubsub.Channel.LIST_MEMBERS, msg)
        return new_member_pk
