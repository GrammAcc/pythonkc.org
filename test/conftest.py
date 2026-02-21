import datetime
import os
from test import (
    mock_data,
    seed,
)

import jwt
import pytest

import pykc


def pytest_sessionstart(session):
    os.environ["APPENV"] = "test"


@pytest.fixture(scope="session")
async def fixt_app():
    """The quart application in dev mode."""

    app = await pykc.async_create_app()
    async with app.test_app() as test_app:
        yield test_app


@pytest.fixture
async def fixt_client(fixt_app):
    """The client used to make requests to the application under test."""

    return fixt_app.test_client()


@pytest.fixture
async def fixt_runner(fixt_app):
    """The CLI test runner for the quart application."""

    return fixt_app.test_cli_runner()


async def _reset_dbs():
    await pykc.dl.db.init(pykc.dl.db.events(), os.environ["EVENTS_DB_URI"], drop_tables=True)
    await pykc.dl.db.init(pykc.dl.db.members(), os.environ["MEMBERS_DB_URI"], drop_tables=True)
    await seed.members()
    await seed.events()


@pytest.fixture(autouse=True, scope="session")
async def init_test_db():
    await _reset_dbs()
    yield


@pytest.fixture(autouse=False)
async def reset_db():
    yield
    await _reset_dbs()


@pytest.fixture
async def fixt_forged_csrf_token():
    now = datetime.datetime.now(datetime.UTC)
    return jwt.encode(
        {"exp": now + datetime.timedelta(days=31), "iat": now},
        "bad_signing_secret",
        algorithm="HS256",
    )


@pytest.fixture
async def fixt_http_headers_valid_csrf():
    return {"X-CSRF-TOKEN": pykc.sl.tokens.generate_csrf()}


@pytest.fixture
async def fixt_ws_headers_valid_csrf():
    return {"Sec-WebSocket-Protocol": f"wamp, csrf{pykc.sl.tokens.generate_csrf()}"}


@pytest.fixture
async def fixt_http_headers_invalid_csrf():
    return {"X-CSRF-TOKEN": pykc.sl.tokens.generate_csrf() + "invalid"}


@pytest.fixture
async def fixt_ws_headers_invalid_csrf():
    return {"Sec-WebSocket-Protocol": f"wamp, csrf{pykc.sl.tokens.generate_csrf() + "invalid"}"}


def _member():
    return mock_data.resources()["seed"]["Member"][0]


def _moderator():
    return mock_data.resources()["seed"]["Member"][1]


def _developer():
    return mock_data.resources()["seed"]["Member"][2]


def _event_manager():
    return mock_data.resources()["seed"]["Member"][3]


def _organizer():
    return mock_data.resources()["seed"]["Member"][4]


@pytest.fixture
def fixt_member():
    return _member()


@pytest.fixture
def fixt_moderator():
    return _moderator()


@pytest.fixture
def fixt_event_manager():
    return _event_manager()


@pytest.fixture
def fixt_developer():
    return _developer()


@pytest.fixture
def fixt_organizer():
    return _organizer()


@pytest.fixture
async def member_session(fixt_client, fixt_member):
    async with fixt_client.session_transaction() as session:
        session["member_id"] = fixt_member["id"]
    yield


@pytest.fixture
async def moderator_session(fixt_client, fixt_moderator):
    async with fixt_client.session_transaction() as session:
        session["member_id"] = fixt_moderator["id"]
    yield


@pytest.fixture
async def developer_session(fixt_client, fixt_developer):
    async with fixt_client.session_transaction() as session:
        session["member_id"] = fixt_developer["id"]
    yield


@pytest.fixture
async def event_manager_session(fixt_client, fixt_event_manager):
    async with fixt_client.session_transaction() as session:
        session["member_id"] = fixt_event_manager["id"]
    yield


@pytest.fixture
async def organizer_session(fixt_client, fixt_organizer):
    async with fixt_client.session_transaction() as session:
        session["member_id"] = fixt_organizer["id"]
    yield


@pytest.fixture
async def fixt_user_session(request, fixt_client):
    async with fixt_client.session_transaction() as session:
        session["member_id"] = globals()["_" + request.param]()["id"]
    yield
