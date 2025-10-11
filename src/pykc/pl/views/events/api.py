import datetime

import grammlog
from quart import (
    Response,
    request,
)

from pykc.constants import MemberPermissions
from pykc.exceptions import PatternError
from pykc.pl import (
    auth,
    dtos,
    res_helpers,
    routes,
    validation,
)
from pykc.sl import (
    errors,
    fetch,
    pubsub,
    scheduling,
)
from pykc.sl.errors import Err
from pykc.types import PK

logger = grammlog.make_logger("crud")


def register_routes():
    @routes.protected_api("/events/venue/<int:venue_id>/delete", methods=["DELETE"])
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def delete_venue(venue_id: PK) -> Response:
        deleted_id = await errors.raise_if_err(scheduling.delete_venue(venue_id))
        msg = {
            "type": pubsub.MsgTypes.LIST_REMOVE,
            "res_id": deleted_id,
        }
        await pubsub.publish(pubsub.Channel.LIST_VENUES, msg)
        return res_helpers.success()

    @routes.protected_api("/events/event/<int:event_id>/cancel", methods=["PATCH"])
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def cancel_event(event_id: PK) -> Response:
        cancelled_event_id = await errors.raise_if_err(scheduling.cancel_event(event_id))
        cancelled_event = await errors.raise_if_err(fetch.event_by_id(cancelled_event_id))
        prepared = validation.prepare(dtos.ListEvent, cancelled_event)
        msg = {
            "type": pubsub.MsgTypes.LIST_UPDATE,
            "res_id": cancelled_event_id,
            "resource": prepared,
        }
        await pubsub.publish(pubsub.Channel.LIST_UPCOMING_EVENTS, msg)
        return res_helpers.success()

    @routes.protected_api("/events/recurring/<int:recurring_id>/delete", methods=["DELETE"])
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def delete_recurring(recurring_id: PK) -> Response:
        deleted_recurring_id, cancelled_event_id = await errors.raise_if_err(
            scheduling.delete_recurring(recurring_id)
        )
        recurring_list_msg = {
            "type": pubsub.MsgTypes.LIST_REMOVE,
            "res_id": deleted_recurring_id,
        }

        cancelled_event = await errors.raise_if_err(fetch.event_by_id(cancelled_event_id))
        prepared = validation.prepare(dtos.ListEvent, cancelled_event)
        event_list_msg = {
            "type": pubsub.MsgTypes.LIST_UPDATE,
            "res_id": cancelled_event_id,
            "resource": prepared,
        }

        await pubsub.publish(pubsub.Channel.LIST_RECURRING, recurring_list_msg)
        await pubsub.publish(pubsub.Channel.LIST_UPCOMING_EVENTS, event_list_msg)
        return res_helpers.success()

    @routes.protected_api("/events/recurring/create", methods=["POST"])
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def create_new_recurring() -> Response:
        payload = await request.json
        if (parsed := validation.sanitize(dtos.CreateRecurring, payload)).success:
            new_recurring_id = await errors.raise_if_err(
                scheduling.create_recurring(recurring_data=parsed.data)
            )
            new_recurring = await errors.raise_if_err(fetch.recurring_by_id(new_recurring_id))
            prepared_recurring = validation.prepare(dtos.ListRecurring, new_recurring)
            new_event = await errors.raise_if_err(
                fetch.next_event_by_recurring_id(new_recurring_id)
            )
            prepared_event = validation.prepare(dtos.ListEvent, new_event)

            recurring_list_msg = {
                "type": pubsub.MsgTypes.LIST_ADD,
                "res_id": new_recurring_id,
                "resource": prepared_recurring,
            }
            event_list_msg = {
                "type": pubsub.MsgTypes.LIST_ADD,
                "res_id": new_event["event_id"],
                "resource": prepared_event,
            }

            await pubsub.publish(pubsub.Channel.LIST_UPCOMING_EVENTS, event_list_msg)
            await pubsub.publish(pubsub.Channel.LIST_RECURRING, recurring_list_msg)

            return res_helpers.created(str(new_recurring_id))
        else:
            return res_helpers.bad_request("validation failed", parsed)

    @routes.protected_api("/events/recurring/<int:recurring_id>/update", methods=["PATCH"])
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def update_recurring_details(recurring_id: PK) -> Response:
        payload = await request.json
        if (parsed := validation.sanitize(dtos.UpdateRecurring, payload)).success:
            updated_recurring = await errors.raise_if_err(
                scheduling.update_recurring(recurring_id, **parsed.data)
            )
            updated = validation.prepare(dtos.UpdateRecurring, updated_recurring)
            changeset_msg = {
                "type": pubsub.MsgTypes.VALIDATION_CHANGESET,
                "saved": [[k, v] for k, v in updated.items()],
                "changed": [],
                "unchanged": [],
            }
            await pubsub.publish(
                pubsub.Channel.VALIDATION_RECURRING, changeset_msg, str(recurring_id)
            )

            prepared_recurring = validation.prepare(dtos.ListRecurring, updated_recurring)
            recurring_list_msg = {
                "type": pubsub.MsgTypes.LIST_UPDATE,
                "res_id": recurring_id,
                "resource": prepared_recurring,
            }
            await pubsub.publish(pubsub.Channel.LIST_RECURRING, recurring_list_msg)

            updated_events = await errors.raise_if_err(
                fetch.upcoming_recurring_events(recurring_id)
            )
            for updated_event in updated_events:
                prepared_event = validation.prepare(dtos.ListEvent, updated_event)

                event_list_msg = {
                    "type": pubsub.MsgTypes.LIST_UPDATE,
                    "res_id": updated_event["event_id"],
                    "resource": prepared_event,
                }

                await pubsub.publish(pubsub.Channel.LIST_UPCOMING_EVENTS, event_list_msg)
            return res_helpers.success()
        else:
            return res_helpers.bad_request("validation failed", parsed)

    @routes.protected_api("/events/event/create", methods=["POST"])
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def create_new_event() -> Response:
        payload = await request.json
        if (parsed := validation.sanitize(dtos.CreateEvent, payload)).success:
            new_event_id = await errors.raise_if_err(
                scheduling.create_event(event_data=parsed.data)
            )
            new_event = await fetch.event_by_id(new_event_id)
            prepared = validation.prepare(dtos.ListEvent, new_event)

            list_update_msg = {
                "type": pubsub.MsgTypes.LIST_ADD,
                "res_id": new_event_id,
                "resource": prepared,
            }

            await pubsub.publish(pubsub.Channel.LIST_UPCOMING_EVENTS, list_update_msg)

            return res_helpers.created(str(new_event_id))
        else:
            return res_helpers.bad_request("validation failed", parsed)

    @routes.protected_api("/events/event/<int:event_id>/update", methods=["PATCH"])
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def update_event_details(event_id: PK) -> Response:
        payload = await request.json
        if (parsed := validation.sanitize(dtos.UpdateEvent, payload)).success:
            updated_event = await errors.raise_if_err(
                scheduling.update_event(event_id, **parsed.data)
            )
            updated = validation.prepare(dtos.UpdateEvent, updated_event)
            changeset_msg = {
                "type": pubsub.MsgTypes.VALIDATION_CHANGESET,
                "saved": [[k, v] for k, v in updated.items()],
                "changed": [],
                "unchanged": [],
            }
            prepared = validation.prepare(dtos.ListEvent, updated_event)
            list_update_msg = {
                "type": pubsub.MsgTypes.LIST_UPDATE,
                "res_id": event_id,
                "resource": prepared,
            }

            await pubsub.publish(pubsub.Channel.VALIDATION_EVENT, changeset_msg, str(event_id))
            await pubsub.publish(pubsub.Channel.LIST_UPCOMING_EVENTS, list_update_msg)
            return res_helpers.success()
        else:
            return res_helpers.bad_request("validation failed", parsed)

    @routes.protected_api("/events/venue/create", methods=["POST"])
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def create_new_venue() -> Response:
        payload = await request.json
        if (parsed := validation.sanitize(dtos.CreateVenue, payload)).success:
            new_venue_id = await errors.raise_if_err(
                scheduling.create_venue(venue_data=parsed.data)
            )
            new_venue = await fetch.venue_by_id(new_venue_id)
            prepared = validation.prepare(dtos.ListVenue, new_venue)

            list_update_msg = {
                "type": pubsub.MsgTypes.LIST_ADD,
                "res_id": new_venue_id,
                "resource": prepared,
            }

            await pubsub.publish(pubsub.Channel.LIST_VENUES, list_update_msg)

            return res_helpers.created(str(new_venue_id))
        else:
            return res_helpers.bad_request("validation failed", parsed)

    @routes.protected_api("/events/venue/<int:venue_id>/update", methods=["PATCH"])
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def update_venue_details(venue_id: PK) -> Response:
        payload = await request.json
        if (parsed := validation.sanitize(dtos.UpdateVenue, payload)).success:
            updated_venue = await errors.raise_if_err(
                scheduling.update_venue(venue_id, **parsed.data)
            )
            updated = validation.prepare(dtos.UpdateVenue, updated_venue)
            changeset_msg = {
                "type": pubsub.MsgTypes.VALIDATION_CHANGESET,
                "saved": [[k, v] for k, v in updated.items()],
                "changed": [],
                "unchanged": [],
            }
            prepared = validation.prepare(dtos.ListVenue, updated_venue)
            list_update_msg = {
                "type": pubsub.MsgTypes.LIST_UPDATE,
                "res_id": venue_id,
                "resource": prepared,
            }

            await pubsub.publish(pubsub.Channel.VALIDATION_VENUE, changeset_msg, str(venue_id))
            await pubsub.publish(pubsub.Channel.LIST_VENUES, list_update_msg)
            return res_helpers.success()
        else:
            return res_helpers.bad_request("validation failed", parsed)

    @routes.protected_api("/events/recurring/<int:recurring_id>/schedule-next", methods=["POST"])
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def schedule_next_event(recurring_id: PK) -> Response:
        recurring_data = await errors.raise_if_err(fetch.recurring_by_id(recurring_id))
        match await errors.return_if_err(fetch.latest_event_by_recurring_id(recurring_id)):
            case Err.OK, dict(anchor_event):
                new_event_id = await errors.raise_if_err(
                    scheduling.schedule_next_event(recurring_data, anchor_event["event_date"])
                )
            case Err.FAILED, _:
                new_event_id = await errors.raise_if_err(
                    scheduling.schedule_next_event(recurring_data, datetime.date.today())
                )
            case _:
                raise PatternError

        new_event = await errors.raise_if_err(fetch.event_by_id(new_event_id))
        prepared = validation.prepare(dtos.ListEvent, new_event)
        list_update_msg = {
            "type": pubsub.MsgTypes.LIST_ADD,
            "res_id": new_event_id,
            "resource": prepared,
        }

        await pubsub.publish(pubsub.Channel.LIST_UPCOMING_EVENTS, list_update_msg)
        return res_helpers.created(str(new_event_id))
