import datetime
import random

from pykc.constants import (
    TIMEZONE,
    EventIntervalType,
    MemberRoles,
)
from pykc.sl import tokens

aug9 = datetime.date(year=2052, month=8, day=9)
aug28 = datetime.date(year=2052, month=8, day=28)
pm7 = datetime.time(hour=19, tzinfo=TIMEZONE)
pm10 = datetime.time(hour=22, tzinfo=TIMEZONE)
am10 = datetime.time(hour=10, tzinfo=TIMEZONE)
noon = datetime.time(hour=12, tzinfo=TIMEZONE)
event_start = datetime.datetime.combine(aug9, am10)
event_end = datetime.datetime.combine(aug9, noon)

api_token = tokens.generate_token(5)
token_hash = tokens.hash_token(api_token)


def mock_oauth_token():
    return "test_oauth_token"


def mock_oauth_state():
    return "mock_oauth_state"


def seed_resources():
    return {
        "Member": [
            {
                "id": 1,
                "moniker": "HT",
                "first_name": "Hugh",
                "last_name": "Test",
                "pronouns": "he/him",
                "permissions": MemberRoles.MEMBER,
                "discord_id": "1",
            },
            {
                "id": 2,
                "moniker": "JT",
                "first_name": "Johnny",
                "last_name": "Test",
                "pronouns": "he/him",
                "permissions": MemberRoles.MODERATOR,
                "discord_id": "2",
            },
            {
                "id": 3,
                "moniker": "ST",
                "first_name": "Susan",
                "last_name": "Test",
                "pronouns": "she/her",
                "permissions": MemberRoles.DEVELOPER,
                "discord_id": "3",
            },
            {
                "id": 4,
                "moniker": "MT",
                "first_name": "Mary",
                "last_name": "Test",
                "pronouns": "she/her",
                "permissions": MemberRoles.EVENT_MANAGER,
                "discord_id": "4",
            },
            {
                "id": 5,
                "moniker": "LT",
                "first_name": "Lila",
                "last_name": "Test",
                "pronouns": "she/her",
                "permissions": MemberRoles.ORGANIZER,
                "discord_id": "5",
            },
            {
                "id": 6,
                "moniker": "DT",
                "first_name": "Dukey",
                "last_name": "Test",
                "pronouns": "he/him",
                "permissions": MemberRoles.ORGANIZER,
                "discord_id": "6",
            },
        ],
        "ApiToken": [
            {
                "id": 1,
                "hash": token_hash,
                "jwt": api_token,
            },
        ],
        "Event": [
            {
                "id": 1,
                "title": "mock_event_title",
                "recurring_id": 1,
                "external_link": "https://www.example.com",
                "description": "mock_event_description",
                "start": datetime.datetime.combine(aug9, am10),
                "end": datetime.datetime.combine(aug9, noon),
                "is_cancelled": False,
                "venue_id": 1,
                "location_details": "room 10",
                "is_av_capable": True,
            },
        ],
        "Recurring": [
            {
                "id": 1,
                "title": "mock_recurring_title",
                "description": "mock_recurring_event_description",
                "interval_type": EventIntervalType.MONTHLY,
                "week": 2,
                "day": 6,
                "start_time": am10,
                "end_time": noon,
            },
        ],
        "Venue": [
            {
                "id": 1,
                "name": "mock_venue_name",
                "address_line1": "12345 Fake Street",
                "city": "Overland Park",
                "state": "KS",
                "postal_code": "66212",
                "external_link": "https://www.example.com",
            },
        ],
    }


def new_resources():
    # Random value to prevent unique constraints from triggering.
    r = str(random.randint(1, 10000))
    base = seed_resources()
    return {
        "Member": {
            **base["Member"][0],
            "moniker": base["Member"][0]["moniker"] + r,
        },
        "ApiToken": {
            **base["ApiToken"][0],
            "hash": base["ApiToken"][0]["hash"] + r,
            "jwt": base["ApiToken"][0]["jwt"] + r,
        },
        "Event": {
            **base["Event"][0],
            "external_link": base["Event"][0]["external_link"] + "/" + r,
        },
        "Recurring": {
            **base["Recurring"][0],
            "title": base["Recurring"][0]["title"] + r,
        },
        "Venue": {
            **base["Venue"][0],
            "name": base["Venue"][0]["name"] + r,
            "external_link": base["Venue"][0]["external_link"] + "/" + r,
        },
    }


def resources():
    return {
        "new": new_resources(),
        "seed": seed_resources(),
    }
