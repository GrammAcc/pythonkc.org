import datetime

import pytest

from pykc.constants import EventIntervalType
from pykc.sl import scheduling

pytestmark = pytest.mark.events

month = 5
week = 3
monday = 1
saturday = 6


# Third Monday of June every year.
yearly_monday = {
    "recurring_interval_type": EventIntervalType.YEARLY,
    "recurring_month": month,
    "recurring_week": week,
    "recurring_day": monday,
}

# Third Monday of the month.
monthly_monday = {
    "recurring_interval_type": EventIntervalType.MONTHLY,
    "recurring_week": week,
    "recurring_day": monday,
}

# Third Monday of the month every quarter.
quarterly_monday = {
    "recurring_interval_type": EventIntervalType.QUARTERLY,
    "recurring_week": week,
    "recurring_day": monday,
}

# Third Monday of the month every half year.
semiyearly_monday = {
    "recurring_interval_type": EventIntervalType.SEMIYEARLY,
    "recurring_week": week,
    "recurring_day": monday,
}

# Weekly on Monday
weekly_monday = {"recurring_interval_type": EventIntervalType.WEEKLY, "recurring_day": monday}


# Third Saturday of June every year.
yearly_saturday = {
    "recurring_interval_type": EventIntervalType.YEARLY,
    "recurring_month": month,
    "recurring_week": week,
    "recurring_day": saturday,
}

# Third Saturday of the month.
monthly_saturday = {
    "recurring_interval_type": EventIntervalType.MONTHLY,
    "recurring_week": week,
    "recurring_day": saturday,
}

# Third Saturday of the month every quarter.
quarterly_saturday = {
    "recurring_interval_type": EventIntervalType.QUARTERLY,
    "recurring_week": week,
    "recurring_day": saturday,
}

# Third Saturday of the month every half year.
semiyearly_saturday = {
    "recurring_interval_type": EventIntervalType.SEMIYEARLY,
    "recurring_week": week,
    "recurring_day": saturday,
}

# Weekly on Saturday
weekly_saturday = {"recurring_interval_type": EventIntervalType.WEEKLY, "recurring_day": saturday}

# Every day.
daily = {"recurring_interval_type": EventIntervalType.DAILY}


async def test_daily():
    """Ensure daily events always give the next date."""

    anchor_date = datetime.date(year=2025, month=6, day=15)
    first = scheduling.compute_next_event_date(daily, anchor_date)
    assert first == datetime.date(year=2025, month=6, day=16)
    second = scheduling.compute_next_event_date(daily, first)
    assert second == datetime.date(year=2025, month=6, day=17)


async def test_weekly_first_week_excluded():
    """1, May 2025 is a Thursday, so the first Monday of the month is the next week."""

    anchor_date = datetime.date(year=2025, month=5, day=15)
    first = scheduling.compute_next_event_date(weekly_monday, anchor_date)
    assert first == datetime.date(year=2025, month=5, day=19)
    second = scheduling.compute_next_event_date(weekly_monday, first)
    assert second == datetime.date(year=2025, month=5, day=26)


async def test_weekly_first_week_included():
    """1, May 2025 is a Thursday, so the first Saturday of the month is in the same week."""

    anchor_date = datetime.date(year=2025, month=5, day=15)
    first = scheduling.compute_next_event_date(weekly_saturday, anchor_date)
    assert first == datetime.date(year=2025, month=5, day=17)
    second = scheduling.compute_next_event_date(weekly_saturday, first)
    assert second == datetime.date(year=2025, month=5, day=24)


async def test_monthly_first_week_excluded():
    """1, May 2025 is a Thursday, so the first Monday of the month is the next week."""

    mock_today = datetime.date(year=2025, month=5, day=15)
    sut = scheduling.compute_next_event_date(monthly_monday, mock_today)
    assert sut == datetime.date(year=2025, month=5, day=19)


async def test_monthly_first_week_included():
    """1, May 2025 is a Thursday, so the first Saturday of the month is in the same week."""

    mock_today = datetime.date(year=2025, month=5, day=15)
    sut = scheduling.compute_next_event_date(monthly_saturday, mock_today)
    assert sut == datetime.date(year=2025, month=5, day=17)


async def test_monthly_rollover_month():
    """Ensure monthly events compute the correct date with the rolled over month when the
    expected event date is earlier in the current month than today's date."""

    mock_today = datetime.date(year=2025, month=5, day=25)
    sut = scheduling.compute_next_event_date(monthly_monday, mock_today)
    assert sut == datetime.date(year=2025, month=6, day=16)


async def test_monthly_rollover_year():
    """Ensure monthly events compute the correct date with the rolled over year when the
    expected event date is earlier in the current month than today's date, and it is
    December."""

    mock_today = datetime.date(year=2025, month=12, day=22)
    sut = scheduling.compute_next_event_date(monthly_monday, mock_today)
    assert sut == datetime.date(year=2026, month=1, day=19)


async def test_quarterly_first_week_exluded():
    """1, Mar 2025 is a Saturday, so the first Monday of the month is the next week."""

    mock_today = datetime.date(year=2025, month=2, day=15)
    sut = scheduling.compute_next_event_date(quarterly_monday, mock_today)
    assert sut == datetime.date(year=2025, month=3, day=17)


async def test_quarterly_first_week_included():
    """1, Mar 2025 is a Saturday, so the first Saturday of the month is the same week."""

    mock_today = datetime.date(year=2025, month=2, day=15)
    sut = scheduling.compute_next_event_date(quarterly_saturday, mock_today)
    assert sut == datetime.date(year=2025, month=3, day=15)


async def test_quarterly_year_rollover():
    """Ensure quarterly events compute the correct date when rolling over into the next year."""

    mock_today = datetime.date(year=2025, month=12, day=22)
    sut = scheduling.compute_next_event_date(quarterly_monday, mock_today)
    assert sut == datetime.date(year=2026, month=3, day=16)


async def test_semiyearly_first_week_exluded():
    """1, June 2024 is a Saturday, so the first Monday of the month is the next week."""

    mock_today = datetime.date(year=2024, month=2, day=15)
    sut = scheduling.compute_next_event_date(semiyearly_monday, mock_today)
    assert sut == datetime.date(year=2024, month=6, day=17)


async def test_semiyearly_first_week_included():
    """1, June 2024 is a Saturday, so the first Saturday of the month is the same week."""

    mock_today = datetime.date(year=2024, month=2, day=15)
    sut = scheduling.compute_next_event_date(semiyearly_saturday, mock_today)
    assert sut == datetime.date(year=2024, month=6, day=15)


async def test_semiyearly_year_rollover():
    """Ensure semiyearly events compute the correct date when rolling over into the next year."""

    mock_today = datetime.date(year=2024, month=12, day=22)
    sut = scheduling.compute_next_event_date(semiyearly_monday, mock_today)
    assert sut == datetime.date(year=2025, month=6, day=16)


async def test_yearly_first_week_excluded():
    """1, May 2025 is a Thursday, so the first Monday of the month is the next week."""

    mock_today = datetime.date(year=2025, month=4, day=15)
    sut = scheduling.compute_next_event_date(yearly_monday, mock_today)
    assert sut == datetime.date(year=2025, month=5, day=19)


async def test_yearly_first_week_included():
    """1, May 2025 is a Thursday, so the first Saturday of the month is in the same week."""

    mock_today = datetime.date(year=2025, month=4, day=15)
    sut = scheduling.compute_next_event_date(yearly_saturday, mock_today)
    assert sut == datetime.date(year=2025, month=5, day=17)


async def test_yearly_rollover():
    """Ensure yearly events compute the correct date with the rolled over year when the
    expected event date is earlier in the current year than today's date."""

    mock_today = datetime.date(year=2025, month=7, day=15)
    sut = scheduling.compute_next_event_date(yearly_monday, mock_today)
    assert sut == datetime.date(year=2026, month=5, day=18)
