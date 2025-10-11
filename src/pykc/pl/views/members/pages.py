from quart import (
    Response,
    redirect,
)
from quart import session as quart_session

from pykc.constants import (
    MemberPermissions,
    MemberRoles,
)
from pykc.pl import (
    auth,
    dtos,
    res_helpers,
    routes,
    utils,
    validation,
)
from pykc.pl.templating import (
    make_url,
    render_template,
)
from pykc.sl import (
    errors,
    fetch,
    tokens,
)
from pykc.sl.errors import Err


def register_routes():
    @routes.public_page("/members", methods=["GET"])
    async def member_list() -> Response:
        members = await errors.raise_if_err(fetch.members())
        return await render_template(
            "pykc/members/index.html.jinja", page_title="Group Members", members=members
        )

    @routes.public_page("/members/<int:member_id>", methods=["GET"])
    async def member_detail(member_id: int) -> Response:
        match await errors.return_if_err(fetch.member_by_id(member_id)):
            case Err.OK, dict(member):
                prepared = validation.prepare(dtos.ListMember, member)
                can_edit = auth.has_permission(MemberPermissions.MODIFY_MEMBER_ROLES)
                return await render_template(
                    "pykc/members/details.html.jinja",
                    page_title=f"Member Profile - {prepared["member_moniker"]}",
                    member=prepared,
                    can_edit=can_edit,
                    all_roles=utils.map_enum_members(MemberRoles),
                )
            case Err.FAILED, Err.QUANTITY:
                return res_helpers.not_found()
            case _:
                return res_helpers.internal_server_error()

    @routes.public_page("/members/login", methods=["GET"])
    async def login_page() -> Response:
        from_logout = False
        if "logout" in quart_session:
            from_logout = True
            quart_session.clear()

        oauth_nonce = tokens.generate_token(60)
        return await render_template(
            "pykc/members/login.html.jinja", from_logout=from_logout, oauth_nonce=oauth_nonce
        )

    @routes.public_page("/members/login/discord", methods=["GET"])
    async def discord_login_page() -> Response:
        return await render_template("pykc/members/discord_login.html.jinja")

    @routes.public_page("/members/join", methods=["GET"])
    async def join_page() -> Response:
        return await render_template("pykc/members/join.html.jinja")

    @routes.protected_page("/members/account", methods=["GET"])
    async def account() -> Response:
        member_id = auth.get_logged_in_member_id()
        member = await errors.raise_if_err(fetch.member_by_id(member_id))
        return await render_template(
            "pykc/members/account.html.jinja", page_title="My Account", member=member
        )

    @routes.protected_page("/members/logout", methods=["GET"])
    async def logout():
        quart_session.clear()
        quart_session["logout"] = True
        return redirect(make_url("/members/login"), code=303)
