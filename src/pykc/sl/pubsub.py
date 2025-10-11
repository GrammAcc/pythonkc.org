"""A rudimentary pubsub implementation."""

import asyncio
import enum
import json

import grammlog

from pykc.common import logs


class MsgTypes(enum.StrEnum):
    LIST_INIT = "INIT_LIST"
    LIST_ADD = "LIST_ADD"
    LIST_REMOVE = ("LIST_REMOVE",)
    LIST_UPDATE = "LIST_UPDATE"
    VALIDATION_INIT = "INIT_VALIDATION"
    VALIDATION_CHANGESET = "CHANGESET"
    VALIDATION_RESULT = "RESULT"
    VALIDATION_FEEDBACK = "VALIDATION"
    LOOPBACK = "LOOPBACK"
    SEARCH_RESULT = "SEARCH_RESULT"


class Channel(enum.IntEnum):
    LIST_MEMBERS = enum.auto()
    LIST_UPCOMING_EVENTS = enum.auto()
    LIST_PAST_EVENTS = enum.auto()
    LIST_RECURRING = enum.auto()
    LIST_VENUES = enum.auto()
    VALIDATION_EVENT = enum.auto()
    VALIDATION_RECURRING = enum.auto()
    VALIDATION_VENUE = enum.auto()
    VALIDATION_ACCOUNT = enum.auto()


_CHANNELS: dict[Channel, dict[str, set[asyncio.Queue]]] = {i: {} for i in list(Channel)}


def subscribe(channel: Channel, filter: str = "default") -> asyncio.Queue:
    """Create an async queue subscribed to a specific pubsub channel.

    The queue returned will be pushed to when calling `publish` on the same
    `channel` + `filter` combination.
    """

    base = _CHANNELS[channel]
    if filter not in base:
        base[filter] = set()

    client_queue = base[filter]
    q: asyncio.Queue = asyncio.Queue()
    client_queue.add(q)
    return q


def unsubscribe(channel: Channel, client: asyncio.Queue, filter: str = "default") -> None:
    """Remove a specific pubsub queue from the selected channel."""

    if filter in _CHANNELS[channel]:
        _CHANNELS[channel][filter].remove(client)
        client.shutdown()
    else:
        grammlog.warning(
            logs.err_log,
            "attempted to unsubscribe from non-existent pubsub channel",
            {
                "domain": "pubsub",
                "caller": unsubscribe.__qualname__,
                "channel": channel,
                "filter": filter,
            },
        )


async def publish(channel: Channel, msg: dict, filter: str = "default") -> None:
    """Broadcast a message to all queues subscribed to the target `channel` + `filter`."""

    base = _CHANNELS[channel]
    if filter not in base:
        await grammlog.async_debug(
            logs.err_log, f"attempted publish to non-existent channel - {channel.name}:{filter}"
        )
    else:
        for q in base[filter]:
            await q.put(json.dumps(msg))
