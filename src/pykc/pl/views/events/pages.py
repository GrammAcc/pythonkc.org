from quart import Response

from pykc.constants import (
    EventIntervalType,
    MemberPermissions,
)
from pykc.pl import (
    auth,
    dtos,
    res_helpers,
    routes,
    validation,
)
from pykc.pl.templating import render_template
from pykc.sl import (
    errors,
    fetch,
)
from pykc.sl.errors import Err


def register_routes():
    @routes.protected_page("/events/manage", methods=["GET"])
    @auth.requires_permission(MemberPermissions.MODIFY_EVENTS)
    async def events_management() -> Response:
        res = await errors.raise_if_err(fetch.events())
        prepared = [validation.prepare(dtos.ListEvent, i) for i in res]
        available_venues = [
            (i["venue_name"], i["venue_id"]) for i in await errors.raise_if_err(fetch.venues())
        ]
        event_intervals = [(i.name.capitalize(), i.value) for i in EventIntervalType]
        weekdays = [
            ("Monday", 1),
            ("Tuesday", 2),
            ("Wednesday", 3),
            ("Thursday", 4),
            ("Friday", 5),
            ("Saturday", 6),
            ("Sunday", 7),
        ]
        months = [
            ("January", 1),
            ("February", 2),
            ("March", 3),
            ("April", 4),
            ("May", 5),
            ("June", 6),
            ("July", 7),
            ("August", 8),
            ("September", 9),
            ("October", 10),
            ("November", 11),
            ("December", 12),
        ]
        weeks = [
            ("First", 1),
            ("Second", 2),
            ("Third", 3),
            ("Fourth", 4),
        ]
        return await render_template(
            "events/manager_dashboard.html.jinja",
            page_title="events-management",
            events=prepared,
            available_venues=available_venues,
            event_intervals=event_intervals,
            weekdays=weekdays,
            weeks=weeks,
            months=months,
        )

    @routes.public_page("/events", methods=["GET"])
    async def events_listing() -> Response:
        res = await errors.raise_if_err(fetch.events())
        prepared = [validation.prepare(dtos.ListEvent, i) for i in res]
        return await render_template(
            "events/events_list.html.jinja", page_title="events", events=prepared
        )

    @routes.public_page("/events/venues", methods=["GET"])
    async def venues_listing() -> Response:
        res = await errors.raise_if_err(fetch.venues())
        prepared = [validation.prepare(dtos.ListVenue, i) for i in res]
        return await render_template(
            "events/venues_list.html.jinja", page_title="venues", venues=prepared
        )

    @routes.public_page("/events/event/<int:event_id>", methods=["GET"])
    async def event_details(event_id: int) -> Response:
        match await errors.return_if_err(fetch.event_by_id(event_id)):
            case Err.OK, dict(res):
                prepared = validation.prepare(dtos.ListEvent, res)
                return await render_template(
                    "events/event_details.html.jinja",
                    page_title="event details",
                    event=prepared,
                )
            case Err.FAILED, Err.QUANTITY:
                return res_helpers.not_found()
            case _:
                return res_helpers.internal_server_error()

    @routes.public_page("/events/venue/<int:venue_id>", methods=["GET"])
    async def venue_details(venue_id: int) -> Response:
        match await errors.return_if_err(fetch.venue_by_id(venue_id)):
            case Err.OK, dict(res):
                prepared = validation.prepare(dtos.ListVenue, res)
                return await render_template(
                    "events/venue_details.html.jinja",
                    page_title="venue details",
                    venue=prepared,
                )
            case Err.FAILED, Err.QUANTITY:
                return res_helpers.not_found()
            case _:
                return res_helpers.internal_server_error()

    @routes.public_page("/events/recurring/<int:recurring_id>", methods=["GET"])
    async def recurring_details(recurring_id: int) -> Response:
        match await errors.return_if_err(fetch.recurring_by_id(recurring_id)):
            case Err.OK, dict(res):
                prepared = validation.prepare(dtos.ListRecurring, res)

                can_edit = auth.has_permission(MemberPermissions.MODIFY_EVENTS)
                interval_types = [[i.name.capitalize(), i.value] for i in list(EventIntervalType)]
                return await render_template(
                    "events/recurring_details.html.jinja",
                    page_title="recurring details",
                    event=prepared,
                    interval_types=interval_types,
                    can_edit=can_edit,
                )
            case Err.FAILED, Err.QUANTITY:
                return res_helpers.not_found()
            case _:
                return res_helpers.internal_server_error()
