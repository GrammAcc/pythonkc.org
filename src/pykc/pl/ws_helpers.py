import asyncio
import json
from collections.abc import (
    Callable,
    Coroutine,
)
from typing import Any

from quart import websocket

from pykc.pl import validation
from pykc.pl.validation.constants import (
    INVALID_SENTINAL,
    OPTIONAL_SENTINAL,
    REQUIRED_SENTINAL,
)
from pykc.pl.validation.contracts import TransformTable
from pykc.sl import (
    errors,
    pubsub,
)
from pykc.sl.errors import Err
from pykc.types import RawData


async def send_from_queue(q: asyncio.Queue):
    while True:
        msg = await q.get()
        await websocket.send(msg)


async def send_validation_init_msg(
    transform: TransformTable, default_data: RawData | None = None
) -> None:
    if default_data is not None:
        fields = validation.prepare(transform, default_data)
    else:
        fields = {k: "" for k in list(transform.prepare)}
    msg = {"type": pubsub.MsgTypes.VALIDATION_INIT, "fields": fields}
    await websocket.send(json.dumps(msg))


async def run_list_socket(
    transform: TransformTable,
    fetch_func: Callable[[], Coroutine[Any, Any, list[RawData]]],
    *event_queues: asyncio.Queue,
) -> None:

    private_queue: asyncio.Queue = asyncio.Queue()

    async def _send_init():
        data = await errors.raise_if_err(fetch_func())
        prepared = [validation.prepare(transform, i) for i in data]
        msg = {
            "type": pubsub.MsgTypes.LIST_INIT,
            "resources": prepared,
        }
        await private_queue.put(json.dumps(msg))

    await websocket.accept(subprotocol="x-none")
    await _send_init()
    pubsub_listeners = [send_from_queue(q) for q in event_queues]
    await asyncio.gather(send_from_queue(private_queue), *pubsub_listeners)


async def run_create_socket(transform: TransformTable, *event_queues: asyncio.Queue) -> None:
    private_queue: asyncio.Queue = asyncio.Queue()

    async def _recv():
        while True:
            msg = json.loads(await websocket.receive())
            sanitized = validation.sanitize(transform, msg)
            failure_messages = sanitized.errors

            validation_errors = {
                "type": pubsub.MsgTypes.VALIDATION_FEEDBACK,
                "success_messages": [],
                "failure_messages": failure_messages,
            }
            await private_queue.put(json.dumps(validation_errors))

            validation_result = {
                "type": pubsub.MsgTypes.VALIDATION_RESULT,
                "success": sanitized.success,
            }
            await private_queue.put(json.dumps(validation_result))

            prepared = validation.prepare(transform, sanitized.data)
            loopback_msg = {
                "type": pubsub.MsgTypes.LOOPBACK,
                "resource": {
                    k: v
                    for k, v in prepared.items()
                    if v not in [OPTIONAL_SENTINAL, INVALID_SENTINAL, REQUIRED_SENTINAL]
                },
            }
            await private_queue.put(json.dumps(loopback_msg))

    await websocket.accept(subprotocol="x-none")
    await send_validation_init_msg(transform)
    pubsub_listeners = [send_from_queue(q) for q in event_queues]
    await asyncio.gather(_recv(), send_from_queue(private_queue), *pubsub_listeners)


async def run_edit_socket(
    transform: TransformTable,
    fetch_func: Callable[[], Coroutine[Any, Any, RawData]],
    *event_queues: asyncio.Queue,
) -> None:
    private_queue: asyncio.Queue = asyncio.Queue()

    async def _recv():
        while True:
            msg = json.loads(await websocket.receive())
            stored = await errors.raise_if_err(fetch_func())
            changeset = validation.changeset(transform, msg, stored)
            changeset_result = {
                "type": pubsub.MsgTypes.VALIDATION_CHANGESET,
                "saved": [],
                "changed": changeset.changed,
                "unchanged": changeset.unchanged,
            }
            changeset_msg = json.dumps(changeset_result)

            await private_queue.put(changeset_msg)

            sanitized = validation.sanitize(transform, msg)
            failure_messages = sanitized.errors

            validation_errors = {
                "type": pubsub.MsgTypes.VALIDATION_FEEDBACK,
                "success_messages": [],
                "failure_messages": failure_messages,
            }
            await private_queue.put(json.dumps(validation_errors))

            validation_result = {
                "type": pubsub.MsgTypes.VALIDATION_RESULT,
                "success": sanitized.success,
            }
            await private_queue.put(json.dumps(validation_result))

            prepared = validation.prepare(transform, sanitized.data)
            loopback_msg = {
                "type": pubsub.MsgTypes.LOOPBACK,
                "resource": {
                    k: v
                    for k, v in prepared.items()
                    if v not in [OPTIONAL_SENTINAL, INVALID_SENTINAL, REQUIRED_SENTINAL]
                },
            }
            await private_queue.put(json.dumps(loopback_msg))

    await websocket.accept(subprotocol="x-none")

    match await errors.return_if_err(fetch_func()):
        case Err.OK, dict(initial_record):
            await send_validation_init_msg(transform, initial_record)
        case Err.FAILED, _:
            await send_validation_init_msg(transform)

    pubsub_listeners = [send_from_queue(q) for q in event_queues]
    await asyncio.gather(_recv(), send_from_queue(private_queue), *pubsub_listeners)
