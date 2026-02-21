__all__ = [
    "ApiToken",
    "COLUMN_ALIASES",
    "Recurring",
    "Event",
    "Member",
    "Venue",
]

from pykc.dl.schemas.events import (
    Event,
    Recurring,
    Venue,
)
from pykc.dl.schemas.members import (
    ApiToken,
    Member,
)

COLUMN_NAMES = {
    "members": [v.label(str(k)) for k, v in Member.c.items()],
    "api_tokens": [v.label(str(k)) for k, v in ApiToken.c.items()],
    "events": [v.label(str(k)) for k, v in Event.c.items()],
    "recurring": [v.label(str(k)) for k, v in Recurring.c.items()],
    "venues": [v.label(str(k)) for k, v in Venue.c.items()],
}
COLUMN_ALIASES = {
    "members": [v.label("member_" + str(k)) for k, v in Member.c.items()],
    "api_tokens": [v.label("api_token_" + str(k)) for k, v in ApiToken.c.items()],
    "events": [v.label("event_" + str(k)) for k, v in Event.c.items()],
    "recurring": [v.label("recurring_" + str(k)) for k, v in Recurring.c.items()],
    "venues": [v.label("venue_" + str(k)) for k, v in Venue.c.items()],
}
