import asyncio
import json

from quart import websocket

from pykc.common import logs
from pykc.pl import (
    auth,
    dtos,
    routes,
    validation,
    ws_helpers,
)
from pykc.sl import (
    errors,
    fetch,
    pubsub,
)
from pykc.sl.errors import Err


def register_routes():
    @routes.public_socket("/members/live/member/list")
    async def list_members_socket():
        channel = pubsub.Channel.LIST_MEMBERS
        q = pubsub.subscribe(channel)

        async def _send_init():
            data = await errors.raise_if_err(fetch.members())
            prepared = [validation.prepare(dtos.ListMember, i) for i in data]
            msg = {
                "type": pubsub.MsgTypes.LIST_INIT,
                "resources": prepared,
            }
            await q.put(json.dumps(msg))

        try:
            await websocket.accept(subprotocol="x-none")
            await _send_init()
            await ws_helpers.send_from_queue(q)
        finally:
            pubsub.unsubscribe(channel, q)

    @routes.protected_socket("/members/live/account/edit")
    async def edit_account_socket():
        member_id = auth.get_logged_in_member_id()
        channel_filter = str(member_id)
        channel = pubsub.Channel.VALIDATION_ACCOUNT

        q = pubsub.subscribe(channel, channel_filter)

        async def _recv():
            while True:
                msg = json.loads(await websocket.receive())
                member_record = await errors.raise_if_err(fetch.member_by_id(member_id))
                changeset = validation.changeset(dtos.UpdateMember, msg, member_record)
                changeset_result = {
                    "type": pubsub.MsgTypes.VALIDATION_CHANGESET,
                    "saved": [],
                    "changed": changeset.changed,
                    "unchanged": changeset.unchanged,
                }
                await q.put(json.dumps(changeset_result))

                sanitized = validation.sanitize(dtos.UpdateMember, msg)
                failure_messages = sanitized.errors
                new_moniker = msg["member_moniker"]
                if new_moniker == member_record["member_moniker"]:
                    validation_msg = {
                        "type": pubsub.MsgTypes.VALIDATION_FEEDBACK,
                        "success_messages": [],
                        "failure_messages": failure_messages,
                    }
                    await q.put(json.dumps(validation_msg))
                else:
                    match await errors.return_if_err(fetch.member_by_moniker(new_moniker)):
                        case Err.OK, _:
                            validation_result = {
                                "type": pubsub.MsgTypes.VALIDATION_FEEDBACK,
                                "success_messages": [],
                                "failure_messages": [
                                    [
                                        "member_moniker",
                                        f"{new_moniker} is already taken",
                                    ],
                                    *failure_messages,
                                ],
                            }
                            await q.put(json.dumps(validation_result))
                        case _, _:
                            validation_result = {
                                "type": pubsub.MsgTypes.VALIDATION_FEEDBACK,
                                "success_messages": [
                                    [
                                        "member_moniker",
                                        f"{new_moniker} is available",
                                    ]
                                ],
                                "failure_messages": failure_messages,
                            }
                            await q.put(json.dumps(validation_result))

        try:
            await websocket.accept(subprotocol="x-none")
            match await errors.return_if_err(fetch.member_by_id(member_id)):
                case Err.OK, dict(member_record):
                    await ws_helpers.send_validation_init_msg(dtos.UpdateMember, member_record)
                case _, _:
                    await ws_helpers.send_validation_init_msg(dtos.UpdateMember)

            await asyncio.gather(_recv(), ws_helpers.send_from_queue(q))
        except Exception as e:
            await logs.log_unknown_error(e, caller=edit_account_socket)
            raise e
        finally:
            pubsub.unsubscribe(channel, q, channel_filter)
