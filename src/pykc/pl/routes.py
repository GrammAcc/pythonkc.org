import functools
from typing import cast

import grammlog
from quart import (
    Blueprint,
    Response,
    g,
    redirect,
    request,
    websocket,
)

from pykc.common import logs
from pykc.pl import (
    auth,
    req_helpers,
    res_helpers,
)
from pykc.pl.templating import make_url
from pykc.sl import tokens
from pykc.sl.errors import Err

bp_public_api = Blueprint("public_api", __name__)
bp_public_pages = Blueprint("public_pages", __name__)
bp_protected_api = Blueprint("protected_api", __name__)
bp_protected_pages = Blueprint("protected_pages", __name__)


async def _login_required() -> Response | None:
    member_id = auth.get_logged_in_member_id_or_none()
    if member_id is None:
        return cast(Response, redirect(make_url("/members/login"), code=303))
    else:
        g.member_id = member_id
        return None


async def _http_validate_csrf() -> Response | None:
    """Ensure the request has a valid CSRF token for all connections."""

    if "x-csrf-token" not in request.headers:
        return res_helpers.forbidden()
    elif tokens.is_token_valid(request.headers["x-csrf-token"]):
        return None
    else:
        return res_helpers.forbidden()


async def _websocket_validate_csrf() -> Response | None:
    """Ensure the websocket handshake has a valid CSRF token for all connections."""

    subps = [i.strip() for i in websocket.headers["sec-websocket-protocol"].split(",")]
    try:
        csrf_token = [i.removeprefix("csrf") for i in subps if i.lower().startswith("csrf")][0]
    except IndexError:
        return res_helpers.forbidden()

    if tokens.is_token_valid(csrf_token):
        return None
    else:
        return res_helpers.forbidden()


async def _ws_auth_required() -> Response | None:
    member_id = auth.get_logged_in_member_id_or_none()
    if member_id is not None:
        # Authenticated browser session.
        g.member_id = member_id
        return None

    else:
        # Check API Keys for request.
        subprotocols = [i.strip() for i in websocket.headers["sec-websocket-protocol"].split(",")]
        try:
            bearer_token = [i for i in subprotocols if i.lower().startswith("bearer")][0]
        except IndexError as e:
            await grammlog.async_debug(
                logs.err_log,
                "Malformed or missing api key in websocket",
                {
                    "domain": "auth",
                    "caller": _ws_auth_required.__qualname__,
                    "headers": str(websocket.headers),
                    "url": websocket.url,
                },
                err=e,
            )
            return res_helpers.unauthorized()
        try:
            api_token = req_helpers.parse_bearer(bearer_token)
            match await tokens.verify_api_key(api_token):
                case Err.OK, str():
                    return None
                case Err.INVALID, str():
                    return res_helpers.unauthorized()
                case _:
                    return res_helpers.unauthorized()
        except Exception as e:
            await grammlog.async_error(
                logs.err_log,
                "Unknown error authenticating websocket with api key",
                {"domain": "auth", "caller": _ws_auth_required.__qualname__, "url": websocket.url},
                err=e,
            )
            return res_helpers.unauthorized()


async def _http_auth_required() -> Response | None:
    member_id = auth.get_logged_in_member_id_or_none()
    if member_id is not None:
        # Authenticated browser session.
        g.member_id = member_id
        return None
    else:
        try:
            # Check API Keys for request.
            if "authorization" not in request.headers:
                return res_helpers.unauthorized()
            api_token = req_helpers.parse_bearer(request.headers["authorization"])
            match await tokens.verify_api_key(api_token):
                case Err.OK, str():
                    return None
                case Err.INVALID, str():
                    return res_helpers.unauthorized()
                case _:
                    return res_helpers.unauthorized()

        except Exception as e:
            await grammlog.async_error(
                logs.err_log,
                "Unknown error authenticating endpoint with api key",
                {"domain": "auth", "caller": _http_auth_required.__qualname__, "url": request.url},
                err=e,
            )
            return res_helpers.unauthorized()


bp_protected_pages.before_request(_login_required)

bp_public_api.before_request(_http_validate_csrf)
bp_public_api.before_websocket(_websocket_validate_csrf)

bp_protected_api.before_request(_http_validate_csrf)
bp_protected_api.before_websocket(_websocket_validate_csrf)
bp_protected_api.before_request(_http_auth_required)
bp_protected_api.before_websocket(_ws_auth_required)


def _register_route(bp, *args, **kwargs):
    def outer(func):
        bp.route(*args, **kwargs)(func)

        @functools.wraps(func)
        async def inner(*iargs, **ikwargs):
            return await func(*iargs, **ikwargs)

        return inner

    return outer


def _register_websocket(bp, *args, **kwargs):
    def outer(func):
        bp.websocket(*args, **kwargs)(func)

        @functools.wraps(func)
        async def inner(*iargs, **ikwargs):
            return await func(*iargs, **ikwargs)

        return inner

    return outer


public_page = functools.partial(_register_route, bp_public_pages)
protected_page = functools.partial(_register_route, bp_protected_pages)
public_api = functools.partial(_register_route, bp_public_api)
protected_api = functools.partial(_register_route, bp_protected_api)
public_socket = functools.partial(_register_websocket, bp_public_api)
protected_socket = functools.partial(_register_websocket, bp_protected_api)
