__all__ = [
    "async_create_app",
    "common",
    "constants",
    "create_app",
    "dl",
    "exceptions",
    "pl",
    "sl",
    "types",
]

import asyncio
import os
from pathlib import Path

import grammlog
from quart import (
    Quart,
    Response,
    jsonify,
)

from . import (
    common,
    constants,
    dl,
    exceptions,
    pl,
    sl,
    types,
)

__version__ = "0.0.1"


ALL_ROUTES: int = 0 | constants.App.EVENTS | constants.App.CONTENT


async def async_create_app() -> Quart:
    """Quart application factory."""

    app = Quart(__name__, instance_relative_config=True)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    app.config.from_mapping(
        {
            "PREFERRED_URL_SCHEME": "https",
            "DEBUG": False,
            "TESTING": os.environ.get("TESTING", False),
            "SECRET_KEY": os.environ["QUART_SECRET"],
        }
    )

    @app.after_serving
    async def cleanup_async_loggers():
        await grammlog.flush()

    # Setup top level routes.
    @app.route("/coffee", methods=["GET"])
    async def coffee() -> Response:
        """Endpoint that returns a status 418 response for compliance
        with the HTCPCP protocol as defined in RFC 2324."""

        res = jsonify(
            {
                "title": "I'm a Teapot",
                "status": 418,
                "detail": f"The {pl.utils.get_domain().removeprefix('https://')} \
coffee pot was replaced with a tea kettle. \
This endpoint is maintained for compliance with the HTCPCP/1.0 standard as defined in RFC 2324.",
                "see_also": "https://www.rfc-editor.org/rfc/rfc2324",
            }
        )
        res.status_code = 418
        res.content_type = "application/problem+json"
        return res

    @app.route("/favicon.ico", methods=["GET"])
    def i_hate_automatic_favicon_requests():
        return Response(status=404)

    @app.route("/robots.txt", methods=["GET"])
    async def robotstxt():
        res = Response("User-agent: *\nDisallow: /", mimetype="text/plain")
        return res

    await _setup_blueprints(app)

    return app


def create_app() -> Quart:
    return asyncio.run(async_create_app())


async def _setup_blueprints(app: Quart) -> None:
    app.template_test()(pl.templating.in_member_permissions)
    app.template_test()(pl.templating.enabled_app)
    app.template_filter()(pl.templating.make_input)
    app.template_filter()(pl.templating.make_textarea)
    app.template_filter()(pl.templating.make_submit)
    app.template_filter()(pl.templating.make_select)
    app.template_filter()(pl.templating.make_info)

    await pl.init(app)
    app.register_blueprint(pl.bp)
