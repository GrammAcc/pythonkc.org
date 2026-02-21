from test import mock_data

import pytest
from quart.testing import WebsocketResponseError

from pykc.constants import MemberRoles
from pykc.pl import utils

pytestmark = pytest.mark.members

ws_urls = [
    "/api/v1/members/live/member/list",
    "/api/v1/members/live/account/edit",
    "/api/v1/members/live/member/create",
]


@pytest.mark.parametrize("ws_url", ws_urls)
async def test_member_socket_requires_csrf(ws_url, fixt_client, fixt_ws_headers_invalid_csrf):
    try:
        async with fixt_client.websocket(ws_url, headers=fixt_ws_headers_invalid_csrf):
            assert False, "Expected rejected connection from websocket"
    except WebsocketResponseError as e:
        assert (
            e.response.status_code == 403
        ), f"Expected status 403 from websocket, got: {e.response.status_code}"


async def test_discord_login_requires_csrf(
    fixt_client, fixt_http_headers_invalid_csrf, fixt_member
):
    payload = {"code": mock_data.mock_oauth_token(), "state": mock_data.mock_oauth_state()}
    res = await fixt_client.put(
        f"{utils.get_site_root()}/api/v1/members/authenticate/discord",
        json=payload,
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


async def test_password_login_requires_csrf(
    fixt_client, fixt_http_headers_invalid_csrf, fixt_member
):
    payload = {"member_pw": mock_data.mock_pw(), "member_moniker": fixt_member["moniker"]}
    res = await fixt_client.put(
        f"{utils.get_site_root()}/api/v1/members/authenticate/password",
        json=payload,
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.parametrize("field_name", ["code", "state"])
async def test_discord_login_missing_required_field(
    field_name, fixt_client, fixt_http_headers_valid_csrf
):
    payload = {"code": mock_data.mock_oauth_token(), "state": mock_data.mock_oauth_state()}
    del payload[field_name]
    res = await fixt_client.put(
        f"{utils.get_site_root()}/api/v1/members/authenticate/discord",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 400


@pytest.mark.parametrize("field_name", ["member_pw", "member_moniker"])
async def test_password_login_missing_required_field(
    field_name, fixt_client, fixt_http_headers_valid_csrf, fixt_member
):
    payload = {"member_pw": mock_data.mock_pw(), "member_moniker": fixt_member["moniker"]}
    del payload[field_name]
    res = await fixt_client.put(
        f"{utils.get_site_root()}/api/v1/members/authenticate/password",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 400


async def test_password_login_success(fixt_client, fixt_http_headers_valid_csrf, fixt_member):
    pw = mock_data.mock_pw()
    moniker = fixt_member["moniker"]
    payload = {"member_pw": pw, "member_moniker": moniker}
    res = await fixt_client.put(
        f"{utils.get_domain()}/api/v1/members/authenticate/password",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 200


async def test_password_login_invalid_pw(fixt_client, fixt_http_headers_valid_csrf, fixt_member):
    pw = mock_data.mock_pw() + "incorrect"
    moniker = fixt_member["moniker"]
    payload = {"member_pw": pw, "member_moniker": moniker}
    res = await fixt_client.put(
        f"{utils.get_domain()}/api/v1/members/authenticate/password",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 400


@pytest.mark.usefixtures("reset_db")
async def test_join_password(fixt_client, fixt_http_headers_valid_csrf):
    payload = {
        "member_pw": "test_password",
        "member_moniker": "test_moniker",
        "member_first_name": "test_first_name",
        "member_last_name": "test_last_name",
    }
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/members/member/create",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 201


async def test_join_password_requires_csrf(fixt_client, fixt_http_headers_invalid_csrf):
    payload = {
        "member_pw": "test_password",
        "member_moniker": "test_moniker",
        "member_first_name": "test_first_name",
        "member_last_name": "test_last_name",
    }
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/members/member/create",
        json=payload,
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.parametrize(
    "field_name", ["member_pw", "member_moniker", "member_first_name", "member_last_name"]
)
async def test_join_password_missing_required_field(
    field_name, fixt_client, fixt_http_headers_valid_csrf
):
    payload = {
        "member_pw": "test_password",
        "member_moniker": "test_moniker",
        "member_first_name": "test_first_name",
        "member_last_name": "test_last_name",
    }
    del payload[field_name]
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/members/member/create",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 400


@pytest.mark.usefixtures("reset_db", "organizer_session")
async def test_change_role(fixt_client, fixt_http_headers_valid_csrf, fixt_member):
    payload = str(int(MemberRoles.MODERATOR))
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/members/member/{fixt_member["id"]}/change-role",
        data=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 200


async def test_change_role_requires_login(fixt_client, fixt_http_headers_valid_csrf, fixt_member):
    payload = str(int(MemberRoles.MODERATOR))
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/members/member/{fixt_member["id"]}/change-role",
        data=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 401


@pytest.mark.usefixtures("organizer_session")
async def test_change_role_requires_csrf(fixt_client, fixt_http_headers_invalid_csrf, fixt_member):
    payload = str(int(MemberRoles.MODERATOR))
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/members/member/{fixt_member["id"]}/change-role",
        data=payload,
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.parametrize(
    "fixt_user_session", ["member", "moderator", "developer", "event_manager"], indirect=True
)
async def test_change_role_requires_organizer_permissions(
    fixt_user_session, fixt_client, fixt_http_headers_valid_csrf, fixt_member
):
    payload = str(int(MemberRoles.ORGANIZER))
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/members/member/{fixt_member["id"]}/change-role",
        data=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("reset_db", "member_session")
async def test_update_account(fixt_client, fixt_http_headers_valid_csrf, fixt_member):
    payload = {
        "member_moniker": "moniker_updated",
        "member_first_name": fixt_member["first_name"],
        "member_last_name": fixt_member["last_name"],
    }
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/members/account/update",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 200


@pytest.mark.usefixtures("member_session")
async def test_update_account_requires_csrf(
    fixt_client, fixt_http_headers_invalid_csrf, fixt_member
):
    payload = {
        "member_moniker": "moniker_updated",
        "member_first_name": fixt_member["first_name"],
        "member_last_name": fixt_member["last_name"],
    }
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/members/account/update",
        json=payload,
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


async def test_update_account_requires_login(
    fixt_client, fixt_http_headers_valid_csrf, fixt_member
):
    payload = {
        "member_moniker": "moniker_updated",
        "member_first_name": fixt_member["first_name"],
        "member_last_name": fixt_member["last_name"],
    }
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/members/account/update",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 401
