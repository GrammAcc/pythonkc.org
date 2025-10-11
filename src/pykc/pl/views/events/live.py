from pykc.constants import MemberPermissions
from pykc.pl import (
    auth,
    dtos,
    routes,
    ws_helpers,
)
from pykc.sl import (
    fetch,
    pubsub,
)
from pykc.types import PK


def register_routes():
    @routes.public_socket("/events/live/venue/list")
    async def list_venues_socket():
        channel = pubsub.Channel.LIST_VENUES
        update_queue = pubsub.subscribe(channel)
        try:
            await ws_helpers.run_list_socket(dtos.ListVenue, fetch.venues, update_queue)
        finally:
            pubsub.unsubscribe(channel, update_queue)

    @routes.public_socket("/events/live/recurring/list")
    async def list_recurring_events_socket():
        channel = pubsub.Channel.LIST_RECURRING
        update_queue = pubsub.subscribe(channel)
        try:
            await ws_helpers.run_list_socket(dtos.ListRecurring, fetch.recurrings, update_queue)
        finally:
            pubsub.unsubscribe(channel, update_queue)

    @routes.public_socket("/events/live/upcoming_event/list")
    async def list_upcoming_events_socket():
        channel = pubsub.Channel.LIST_UPCOMING_EVENTS
        update_queue = pubsub.subscribe(channel)
        try:
            await ws_helpers.run_list_socket(dtos.ListEvent, fetch.upcoming_events, update_queue)
        finally:
            pubsub.unsubscribe(channel, update_queue)

    @routes.public_socket("/events/live/past_event/list")
    async def list_past_events_socket():
        channel = pubsub.Channel.LIST_PAST_EVENTS
        update_queue = pubsub.subscribe(channel)
        try:
            await ws_helpers.run_list_socket(dtos.ListEvent, fetch.past_events, update_queue)
        finally:
            pubsub.unsubscribe(channel, update_queue)

    @routes.protected_socket("/events/live/recurring/<int:recurring_id>/edit")
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def edit_recurring_socket(recurring_id: PK):
        channel_filter = str(recurring_id)
        channel = pubsub.Channel.VALIDATION_RECURRING
        update_queue = pubsub.subscribe(channel, channel_filter)
        try:
            await ws_helpers.run_edit_socket(
                dtos.UpdateRecurring,
                lambda: fetch.recurring_by_id(recurring_id),
                update_queue,
            )
        finally:
            pubsub.unsubscribe(channel, update_queue, channel_filter)

    @routes.protected_socket("/events/live/recurring/create")
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def create_recurring_socket():
        channel = pubsub.Channel.LIST_UPCOMING_EVENTS
        update_queue = pubsub.subscribe(channel)
        try:
            await ws_helpers.run_create_socket(dtos.CreateRecurring, update_queue)
        finally:
            pubsub.unsubscribe(channel, update_queue)

    @routes.protected_socket("/events/live/event/<int:event_id>/edit")
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def edit_event_socket(event_id: PK):
        channel_filter = str(event_id)
        channel = pubsub.Channel.VALIDATION_EVENT
        update_queue = pubsub.subscribe(channel, channel_filter)
        try:
            await ws_helpers.run_edit_socket(
                dtos.UpdateEvent,
                lambda: fetch.event_by_id(event_id),
                update_queue,
            )
        finally:
            pubsub.unsubscribe(channel, update_queue, channel_filter)

    @routes.protected_socket("/events/live/event/create")
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def create_event_socket():
        channel = pubsub.Channel.LIST_UPCOMING_EVENTS
        update_queue = pubsub.subscribe(channel)
        try:
            await ws_helpers.run_create_socket(dtos.CreateEvent, update_queue)
        finally:
            pubsub.unsubscribe(channel, update_queue)

    @routes.protected_socket("/events/live/venue/<int:venue_id>/edit")
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def edit_venue_socket(venue_id: PK):
        channel_filter = str(venue_id)
        channel = pubsub.Channel.VALIDATION_VENUE
        update_queue = pubsub.subscribe(channel, channel_filter)
        try:
            await ws_helpers.run_edit_socket(
                dtos.UpdateVenue,
                lambda: fetch.venue_by_id(venue_id),
                update_queue,
            )
        finally:
            pubsub.unsubscribe(channel, update_queue, channel_filter)

    @routes.protected_socket("/events/live/venue/create")
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def create_venue_socket():
        channel = pubsub.Channel.LIST_VENUES
        update_queue = pubsub.subscribe(channel)
        try:
            await ws_helpers.run_create_socket(dtos.CreateVenue, update_queue)
        finally:
            pubsub.unsubscribe(channel, update_queue)
