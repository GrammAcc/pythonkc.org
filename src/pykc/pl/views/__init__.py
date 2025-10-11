__all__ = [
    "events",
    "members",
    "register_routes",
]

import asyncio
import json

from quart import (
    Response,
    websocket,
)

from pykc.common import logs
from pykc.pl import (
    dtos,
    routes,
    validation,
    ws_helpers,
)
from pykc.pl.templating import render_template
from pykc.sl import (
    errors,
    fetch,
    pubsub,
)

from . import (
    events,
    members,
)


def register_routes():
    @routes.public_page("/", methods=["GET"])
    async def index() -> Response:
        return await render_template("pykc/index.html.jinja", page_title="home")

    @routes.public_page("/about", methods=["GET"])
    async def about() -> Response:
        return await render_template("pykc/about.html.jinja", page_title="About PyKC")

    @routes.public_socket("/live/quicksearch")
    async def quicksearch_socket() -> None:

        private_queue: asyncio.Queue = asyncio.Queue()

        empty_results_msg = {
            "type": pubsub.MsgTypes.SEARCH_RESULT,
            "members": [],
            "events": [],
        }

        async def _recv():
            while True:
                try:
                    msg = await websocket.receive()
                    if msg == "":
                        await private_queue.put(json.dumps(empty_results_msg))
                    else:
                        members, events = await asyncio.gather(
                            errors.raise_if_err(fetch.search_members(msg)),
                            errors.raise_if_err(fetch.search_events(msg)),
                        )
                        prepared_events = [validation.prepare(dtos.ListEvent, i) for i in events]
                        prepared_members = [validation.prepare(dtos.ListMember, i) for i in members]

                        search_result_msg = {
                            "type": pubsub.MsgTypes.SEARCH_RESULT,
                            "members": prepared_members,
                            "events": prepared_events,
                        }
                        await private_queue.put(json.dumps(search_result_msg))
                except Exception as e:
                    await logs.log_unknown_error(e, caller=quicksearch_socket)

        await websocket.accept(subprotocol="x-none")
        await private_queue.put(json.dumps(empty_results_msg))

        await asyncio.gather(_recv(), ws_helpers.send_from_queue(private_queue))
