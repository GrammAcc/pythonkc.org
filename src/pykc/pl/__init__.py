__all__ = [
    "auth",
    "bp",
    "dtos",
    "req_helpers",
    "res_helpers",
    "routes",
    "templating",
    "utils",
    "validation",
    "views",
    "ws_helpers",
]

from quart import (
    Blueprint,
    Quart,
    g,
)

from pykc.constants import App
from pykc.sl import (
    errors,
    fetch,
    init_app,
)
from pykc.sl.errors import Err

from . import (
    auth,
    dtos,
    req_helpers,
    res_helpers,
    routes,
    templating,
    utils,
    validation,
    views,
    ws_helpers,
)

bp = Blueprint(
    "pykc",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/pykc/static",
)
"""/"""


bp.register_blueprint(routes.bp_protected_api, url_prefix="/api/v1")
bp.register_blueprint(routes.bp_public_api, url_prefix="/api/v1")
bp.register_blueprint(routes.bp_public_pages)
bp.register_blueprint(routes.bp_protected_pages)


async def load_permissions() -> None:
    member_id = auth.get_logged_in_member_id_or_none()
    if member_id is not None:
        match await errors.return_if_err(fetch.member_permissions(member_id)):
            case Err.OK, permissions:
                g.member_permissions = permissions
            case Err.FAILED, _:
                raise ValueError(f"permissions not found for member_id: {member_id}")
    return None


bp.before_request(load_permissions)
bp.before_websocket(load_permissions)


async def init(app: Quart) -> None:
    views.register_routes()

    if utils.is_app_enabled(App.MEMBERS):
        views.members.register_routes()
        await init_app(App.MEMBERS)

    if utils.is_app_enabled(App.EVENTS):
        views.events.register_routes()
        await init_app(App.EVENTS)
