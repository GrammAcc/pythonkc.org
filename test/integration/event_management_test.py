from test import mock_data

import pytest
from quart.testing import WebsocketResponseError

from pykc.pl import (
    dtos,
    utils,
    validation,
)

pytestmark = pytest.mark.events

ws_urls = [
    "/api/v1/events/live/upcoming_event/list",
    "/api/v1/events/live/past_event/list",
    "/api/v1/events/live/venue/list",
    "/api/v1/events/live/recurring/list",
    "/api/v1/events/live/event/create",
    "/api/v1/events/live/venue/create",
    "/api/v1/events/live/recurring/create",
    "/api/v1/events/live/event/1/edit",
    "/api/v1/events/live/venue/1/edit",
    "/api/v1/events/live/recurring/1/edit",
]


@pytest.mark.parametrize("ws_url", ws_urls)
async def test_event_management_socket_requires_csrf(
    ws_url, fixt_client, fixt_ws_headers_invalid_csrf
):
    try:
        async with fixt_client.websocket(ws_url, headers=fixt_ws_headers_invalid_csrf):
            assert False, "Expected rejected connection from websocket"
    except WebsocketResponseError as e:
        assert (
            e.response.status_code == 403
        ), f"Expected status 403 from websocket, got: {e.response.status_code}"


def create_event_payload():
    base = mock_data.resources()["new"]["Event"]
    return validation.prepare(
        dtos.CreateEvent,
        {
            **{"event_" + k: v for k, v in base.items()},
            "event_date": base["start"].date(),
            "event_start_time": base["start"].time(),
            "event_end_time": base["end"].time(),
        },
    )


def update_event_payload():
    return {**create_event_payload(), "event_title": "updated_title"}


def create_venue_payload():
    base = mock_data.resources()["new"]["Venue"]
    return validation.prepare(dtos.CreateVenue, {"venue_" + k: v for k, v in base.items()})


def update_venue_payload():
    return {**create_venue_payload(), "venue_name": "updated_name"}


def create_recurring_payload():
    base = mock_data.resources()["new"]["Recurring"]
    return validation.prepare(dtos.CreateRecurring, {"recurring_" + k: v for k, v in base.items()})


def update_recurring_payload():
    return {**create_recurring_payload(), "recurring_title": "updated_title"}


@pytest.mark.usefixtures("event_manager_session")
async def test_create_event_requires_csrf(fixt_client, fixt_http_headers_invalid_csrf):
    payload = create_event_payload()
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/events/event/create",
        json=payload,
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("reset_db", "event_manager_session")
async def test_create_event_success(fixt_client, fixt_http_headers_valid_csrf):
    payload = create_event_payload()
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/events/event/create",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 201


@pytest.mark.parametrize("fixt_user_session", ["member", "moderator", "developer"], indirect=True)
async def test_create_event_requires_event_manager_permissions(
    fixt_user_session, fixt_client, fixt_http_headers_valid_csrf
):
    payload = create_event_payload()
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/events/event/create",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("event_manager_session")
async def test_create_venue_requires_csrf(fixt_client, fixt_http_headers_invalid_csrf):
    payload = create_venue_payload()
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/events/venue/create",
        json=payload,
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("reset_db", "event_manager_session")
async def test_create_venue_success(fixt_client, fixt_http_headers_valid_csrf):
    payload = create_venue_payload()
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/events/venue/create",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 201


@pytest.mark.parametrize("fixt_user_session", ["member", "moderator", "developer"], indirect=True)
async def test_create_venue_requires_event_manager_permissions(
    fixt_user_session, fixt_client, fixt_http_headers_valid_csrf
):
    payload = create_venue_payload()
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/events/venue/create",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("event_manager_session")
async def test_create_recurring_requires_csrf(fixt_client, fixt_http_headers_invalid_csrf):
    payload = create_recurring_payload()
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/events/recurring/create",
        json=payload,
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("reset_db", "event_manager_session")
async def test_create_recurring_success(fixt_client, fixt_http_headers_valid_csrf):
    payload = create_recurring_payload()
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/events/recurring/create",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 201


@pytest.mark.parametrize("fixt_user_session", ["member", "moderator", "developer"], indirect=True)
async def test_create_recurring_requires_event_manager_permissions(
    fixt_user_session, fixt_client, fixt_http_headers_valid_csrf
):
    payload = create_recurring_payload()
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/events/recurring/create",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("event_manager_session")
async def test_update_event_requires_csrf(fixt_client, fixt_http_headers_invalid_csrf):
    target_event = mock_data.resources()["seed"]["Event"][0]
    payload = update_event_payload()
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/events/event/{target_event["id"]}/update",
        json=payload,
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("reset_db", "event_manager_session")
async def test_update_event_success(fixt_client, fixt_http_headers_valid_csrf):
    payload = update_event_payload()
    target_event = mock_data.resources()["seed"]["Event"][0]
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/events/event/{target_event["id"]}/update",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 200


@pytest.mark.parametrize("fixt_user_session", ["member", "moderator", "developer"], indirect=True)
async def test_update_event_requires_event_manager_permissions(
    fixt_user_session, fixt_client, fixt_http_headers_valid_csrf
):
    payload = update_event_payload()
    target_event = mock_data.resources()["seed"]["Event"][0]
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/events/event/{target_event["id"]}/update",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("event_manager_session")
async def test_update_venue_requires_csrf(fixt_client, fixt_http_headers_invalid_csrf):
    target_venue = mock_data.resources()["seed"]["Venue"][0]
    payload = update_venue_payload()
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/events/venue/{target_venue["id"]}/update",
        json=payload,
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("reset_db", "event_manager_session")
async def test_update_venue_success(fixt_client, fixt_http_headers_valid_csrf):
    target_venue = mock_data.resources()["seed"]["Venue"][0]
    payload = update_venue_payload()
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/events/venue/{target_venue["id"]}/update",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 200


@pytest.mark.parametrize("fixt_user_session", ["member", "moderator", "developer"], indirect=True)
async def test_update_venue_requires_event_manager_permissions(
    fixt_user_session, fixt_client, fixt_http_headers_valid_csrf
):
    target_venue = mock_data.resources()["seed"]["Venue"][0]
    payload = update_venue_payload()
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/events/venue/{target_venue["id"]}/update",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("event_manager_session")
async def test_update_recurring_requires_csrf(fixt_client, fixt_http_headers_invalid_csrf):
    target_recurring = mock_data.resources()["seed"]["Recurring"][0]
    payload = update_recurring_payload()
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/events/recurring/{target_recurring["id"]}/update",
        json=payload,
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("reset_db", "event_manager_session")
async def test_update_recurring_success(fixt_client, fixt_http_headers_valid_csrf):
    target_recurring = mock_data.resources()["seed"]["Recurring"][0]
    payload = update_recurring_payload()
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/events/recurring/{target_recurring["id"]}/update",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 200


@pytest.mark.parametrize("fixt_user_session", ["member", "moderator", "developer"], indirect=True)
async def test_update_recurring_requires_event_manager_permissions(
    fixt_user_session, fixt_client, fixt_http_headers_valid_csrf
):
    target_recurring = mock_data.resources()["seed"]["Recurring"][0]
    payload = update_recurring_payload()
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/events/recurring/{target_recurring["id"]}/update",
        json=payload,
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("event_manager_session")
async def test_cancel_event_requires_csrf(fixt_client, fixt_http_headers_invalid_csrf):
    target_event = mock_data.resources()["seed"]["Event"][0]
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/events/event/{target_event["id"]}/cancel",
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("reset_db", "event_manager_session")
async def test_cancel_event_success(fixt_client, fixt_http_headers_valid_csrf):
    target_event = mock_data.resources()["seed"]["Event"][0]
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/events/event/{target_event["id"]}/cancel",
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 200


@pytest.mark.parametrize("fixt_user_session", ["member", "moderator", "developer"], indirect=True)
async def test_cancel_event_requires_event_manager_permissions(
    fixt_user_session, fixt_client, fixt_http_headers_valid_csrf
):
    target_event = mock_data.resources()["seed"]["Event"][0]
    res = await fixt_client.patch(
        f"{utils.get_site_root()}/api/v1/events/event/{target_event["id"]}/cancel",
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("event_manager_session")
async def test_delete_venue_requires_csrf(fixt_client, fixt_http_headers_invalid_csrf):
    target_venue = mock_data.resources()["seed"]["Venue"][0]
    res = await fixt_client.delete(
        f"{utils.get_site_root()}/api/v1/events/venue/{target_venue["id"]}/delete",
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("reset_db", "event_manager_session")
async def test_delete_venue_success(fixt_client, fixt_http_headers_valid_csrf):
    target_venue = mock_data.resources()["seed"]["Venue"][0]
    res = await fixt_client.delete(
        f"{utils.get_site_root()}/api/v1/events/venue/{target_venue["id"]}/delete",
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 200


@pytest.mark.parametrize("fixt_user_session", ["member", "moderator", "developer"], indirect=True)
async def test_delete_venue_requires_event_manager_permissions(
    fixt_user_session, fixt_client, fixt_http_headers_valid_csrf
):
    target_venue = mock_data.resources()["seed"]["Venue"][0]
    res = await fixt_client.delete(
        f"{utils.get_site_root()}/api/v1/events/venue/{target_venue["id"]}/delete",
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("event_manager_session")
async def test_delete_recurring_requires_csrf(fixt_client, fixt_http_headers_invalid_csrf):
    target_recurring = mock_data.resources()["seed"]["Recurring"][0]
    res = await fixt_client.delete(
        f"{utils.get_site_root()}/api/v1/events/recurring/{target_recurring["id"]}/delete",
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("reset_db", "event_manager_session")
async def test_delete_recurring_success(fixt_client, fixt_http_headers_valid_csrf):
    target_recurring = mock_data.resources()["seed"]["Recurring"][0]
    res = await fixt_client.delete(
        f"{utils.get_site_root()}/api/v1/events/recurring/{target_recurring["id"]}/delete",
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 200


@pytest.mark.parametrize("fixt_user_session", ["member", "moderator", "developer"], indirect=True)
async def test_delete_recurring_requires_event_manager_permissions(
    fixt_user_session, fixt_client, fixt_http_headers_valid_csrf
):
    target_recurring = mock_data.resources()["seed"]["Recurring"][0]
    res = await fixt_client.delete(
        f"{utils.get_site_root()}/api/v1/events/recurring/{target_recurring["id"]}/delete",
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("event_manager_session")
async def test_schedule_next_event_requires_csrf(fixt_client, fixt_http_headers_invalid_csrf):
    target_recurring = mock_data.resources()["seed"]["Recurring"][0]
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/events/recurring/{target_recurring["id"]}/schedule-next",
        headers=fixt_http_headers_invalid_csrf,
    )
    assert res.status_code == 403


@pytest.mark.usefixtures("reset_db", "event_manager_session")
async def test_schedule_next_event_success(fixt_client, fixt_http_headers_valid_csrf):
    target_recurring = mock_data.resources()["seed"]["Recurring"][0]
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/events/recurring/{target_recurring["id"]}/schedule-next",
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 201


@pytest.mark.parametrize("fixt_user_session", ["member", "moderator", "developer"], indirect=True)
async def test_schedule_next_event_requires_event_manager_permissions(
    fixt_user_session, fixt_client, fixt_http_headers_valid_csrf
):
    target_recurring = mock_data.resources()["seed"]["Recurring"][0]
    res = await fixt_client.post(
        f"{utils.get_site_root()}/api/v1/events/recurring/{target_recurring["id"]}/schedule-next",
        headers=fixt_http_headers_valid_csrf,
    )
    assert res.status_code == 403
