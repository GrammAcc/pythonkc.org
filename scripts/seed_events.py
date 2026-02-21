import asyncio
import datetime
import os

import grammdb

from pykc.common import appenv
from pykc.constants import (
    TIMEZONE,
    EventIntervalType,
)
from pykc.dl import (
    crud,
    db,
)
from pykc.sl import scheduling

appenv.load()

aug9 = datetime.date(year=2025, month=8, day=9)
aug28 = datetime.date(year=2025, month=8, day=28)
pm7 = datetime.time(hour=19, tzinfo=TIMEZONE)
pm10 = datetime.time(hour=22, tzinfo=TIMEZONE)
am10 = datetime.time(hour=10, tzinfo=TIMEZONE)
noon = datetime.time(hour=12, tzinfo=TIMEZONE)
coffee_and_code_event_start = datetime.datetime.combine(aug9, am10)
coffee_and_code_event_end = datetime.datetime.combine(aug9, noon)
summer_meetup_event_start = datetime.datetime.combine(aug28, pm7)
summer_meetup_event_end = datetime.datetime.combine(aug28, pm10)

summer_meetup_link = "https://www.meetup.com/pythonkc/events/fggfxlyhclblc"
quarterly_meetup_title = "PythonKC Quarterly Meetup"
quartarly_meetup_desc = "RSVPs will open two weeks before the meetup."

coffee_and_code_meetup_link = "https://www.meetup.com/pythonkc/events/308665802"

coffee_and_code_title = "PythonKC Coffee & Code"
coffee_and_code_desc = """
RSVPs open 10 days before the date of the event.

Come work on Python projects, get programming help, help others, and meet interesting people. We'll begin with brief introductions and an opportunity to talk about what we're each working on. We'll have members available to help beginning Python programmers with language basics and getting Python and related tools installed on their computers. We'll have plenty of time for more advanced topics, too.

Audience: Everyone! We'll have something for all Python experience levels.

What to bring: A laptop with WiFi and power cord.
"""


async def run():
    await db.init(db.events(), os.environ["EVENTS_DB_URI"], drop_tables=True, echo=True)
    coffee_and_code_id = await scheduling.create_recurring(
        recurring_data={
            "recurring_title": coffee_and_code_title,
            "recurring_description": coffee_and_code_desc,
            "recurring_interval_type": EventIntervalType.MONTHLY,
            "recurring_week": 2,
            "recurring_day": 6,
            "recurring_start_time": am10,
            "recurring_end_time": noon,
        }
    )
    quarterly_meetup_id = await scheduling.create_recurring(
        recurring_data={
            "recurring_title": quarterly_meetup_title,
            "recurring_description": quartarly_meetup_desc,
            "recurring_interval_type": EventIntervalType.QUARTERLY,
            "recurring_week": 3,
            "recurring_day": 4,
            "recurring_start_time": pm7,
            "recurring_end_time": pm10,
        }
    )
    tr = await grammdb.start_transaction(db.events())
    library_id = await crud.create_venue(
        tr,
        name="Johnson County Central Resource Library",
        address_line1="9875 W 87th St",
        city="Overland Park",
        state="KS",
        postal_code="66212",
        external_link="https://www.jocolibrary.org/locations/central/",
    )
    keystone_id = await crud.create_venue(
        tr,
        name="Keystone CoLab",
        address_line1="800 E 18th St",
        city="Kansas City",
        state="MO",
        postal_code="64108",
        external_link="https://www.keystonedistrict.org/",
    )
    c_and_c_event_id = (await crud.get_next_recurring_event(tr, coffee_and_code_id)).id
    await crud.update_event(
        tr, c_and_c_event_id, venue_id=library_id, location_details="Room #20", is_av_capable=True
    )
    summer_meetup_id = (await crud.get_next_recurring_event(tr, quarterly_meetup_id)).id
    await crud.update_event(
        tr,
        summer_meetup_id,
        venue_id=keystone_id,
        location_details="Main Stage",
        is_av_capable=True,
    )

    await grammdb.commit_transaction(tr)


asyncio.run(run())
