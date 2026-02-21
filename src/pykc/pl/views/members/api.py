from quart import (
    Response,
    request,
)
from quart import session as quart_session

from pykc.common import logs
from pykc.constants import MemberPermissions
from pykc.exceptions import DataError
from pykc.pl import (
    auth,
    dtos,
    res_helpers,
    routes,
    validation,
)
from pykc.sl import (
    acl,
    errors,
    fetch,
    pubsub,
    tokens,
)
from pykc.sl.errors import Err
from pykc.types import PK

from . import oauth


def register_routes():
    @routes.public_api("/members/authenticate/password", methods=["PUT"])
    async def password_authentication() -> Response:
        """Login the user with password auth."""

        body = await request.get_json()
        if not (sanitized := validation.sanitize(dtos.MemberLogin, body)).success:
            return res_helpers.bad_request("validation failed", sanitized)
        else:
            moniker, pw = sanitized.data["member_moniker"], sanitized.data["member_pw"]

            match await tokens.verify_member_password(moniker, pw):
                case Err.OK, member_id:
                    quart_session["member_id"] = member_id
                    quart_session.permanent = True
                    return res_helpers.success()
                case Err.INVALID, str(result):
                    return res_helpers.bad_request(result)
                case Err.AUTH, str():
                    return res_helpers.unauthorized()
                case _:
                    return res_helpers.internal_server_error()

    @routes.public_api("/members/member/create", methods=["POST"])
    async def create_member() -> Response:
        payload = await request.json
        if not (sanitized := validation.sanitize(dtos.CreateMember, payload)).success:
            return res_helpers.bad_request("create member failed", sanitized)
        else:
            match await errors.return_if_err(acl.create_member_with_password(**sanitized.data)):
                case Err.OK, new_member_pk:
                    new_member = await errors.raise_if_err(fetch.member_by_id(new_member_pk))
                    prepared = validation.prepare(dtos.CreateMember, new_member)
                    msg = {
                        "type": pubsub.MsgTypes.LIST_ADD,
                        "res_id": new_member_pk,
                        "resource": prepared,
                    }
                    await pubsub.publish(pubsub.Channel.LIST_MEMBERS, msg)
                    return res_helpers.created(str(new_member_pk))
                case Err.INTEGRITY:
                    return res_helpers.bad_request("bad data")
                case _:
                    return res_helpers.internal_server_error()

    @routes.public_api("/members/authenticate/discord", methods=["PUT"])
    async def discord_authentication() -> Response:
        """Login the user with discord."""
        body = await request.json
        if not (sanitized := validation.sanitize(dtos.DiscordLogin, body)).success:
            return res_helpers.bad_request("validation failed", sanitized)

        discord_access_code = sanitized.data["code"]
        discord_oauth_state = sanitized.data["state"]
        if not tokens.is_token_valid(discord_oauth_state):
            await logs.log_oauth_error("oauth state token invalid", discord_authentication)
            return res_helpers.unauthorized()

        status, res = await oauth.discord_exchange_code(discord_access_code, discord_oauth_state)
        # TODO: Setup automatic token refresh.

        if status != 200:
            await logs.log_oauth_error(
                "initial token request failed",
                oauth.discord_exchange_code,
                status=status,
                response=res,
            )
            return res_helpers.unauthorized()

        user_res_status, user_data = await oauth.discord_get_user_profile(res["access_token"])
        if user_res_status == 404 and user_data.get("code", 0) == 10004:
            return res_helpers.bad_request("You must be a member of the pykc discord to log in")
        if user_res_status != 200:
            await logs.log_oauth_error(
                "user data request failed",
                oauth.discord_get_user_profile,
                status=user_res_status,
                response=user_data,
            )
            return res_helpers.unauthorized()

        match await errors.return_if_err(fetch.member_by_discord_id(str(user_data["user"]["id"]))):
            case Err.OK, dict(member):
                quart_session["member_id"] = member["member_id"]
                quart_session.permanent = True
                return res_helpers.success()
            case Err.FAILED, Err.QUANTITY:
                try:
                    new_member_id = await errors.raise_if_err(
                        oauth.create_member_from_discord(user_data)
                    )
                    quart_session["member_id"] = new_member_id
                    quart_session.permanent = True
                    return res_helpers.success()
                except DataError as e:
                    await logs.log_oauth_error(
                        "create new user from discord data failed",
                        oauth.create_member_from_discord,
                        err=e,
                    )
                    return res_helpers.unauthorized()
            case _:
                return res_helpers.internal_server_error()

    @routes.protected_api("/members/member/<int:member_id>/change-role", methods=["PATCH"])
    @auth.requires_permission(MemberPermissions.MODIFY_MEMBER_ROLES)
    async def update_member_role(member_id: PK) -> Response:
        role_bit_string = await request.body
        payload = {"member_permissions": role_bit_string}
        if not (sanitized := validation.sanitize(dtos.UpdateMemberPermissions, payload)).success:
            return res_helpers.bad_request("validation failed", sanitized)
        else:
            new_permissions = sanitized.data["member_permissions"]
            await errors.raise_if_err(acl.set_member_role(member_id, new_permissions))
            return res_helpers.success()

    @routes.protected_api("/members/account/update", methods=["PATCH"])
    async def update_member_account() -> Response:
        member_id = auth.get_logged_in_member_id()
        payload = await request.json
        if not (sanitized := validation.sanitize(dtos.UpdateMember, payload)).success:
            return res_helpers.bad_request("validation failed", sanitized)
        else:
            result = await errors.raise_if_err(acl.update_member(member_id, **sanitized.data))
            msg = {
                "type": "CHANGESET",
                "saved": [[k, v] for k, v in result.items()],
                "changed": [],
                "unchanged": [],
            }
            await pubsub.publish(pubsub.Channel.VALIDATION_ACCOUNT, msg, str(member_id))
            return res_helpers.success()
