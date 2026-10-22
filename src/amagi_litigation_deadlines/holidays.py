"""Legal holiday calculators.

Two holiday sets are implemented, matching the two bundled rule sets:

- ``federal_holidays(year)``: the holidays listed in 5 U.S.C. S 6103, which
  Fed. R. Civ. P. 6(a)(6)(A) incorporates by reference as "legal holidays"
  for the purpose of the federal day-counting rule. 5 U.S.C. S 6103(b)
  provides that when a fixed-date holiday falls on a Saturday, it is
  observed the preceding Friday, and when it falls on a Sunday, it is
  observed the following Monday.
- ``florida_holidays(year)``: the holidays listed in Fla. Stat. S 683.01,
  which Fla. R. Jud. Admin. 2.514(a)(6) incorporates by reference as "legal
  holidays" for the state day-counting rule. Florida's statute does not
  itself shift fixed-date holidays off weekends, so no Friday/Monday
  observed-date shift is applied here.

These lists are a best-effort, code-maintained approximation of each
statute as of 2026-10-20. Always verify the current holiday list against
the statute and against the specific court's published calendar -- a court
can be closed (and the clock can therefore still extend) for a day that
is not on this list, e.g. a local closure order.
"""

from __future__ import annotations

import datetime as _dt


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> _dt.date:
    """Return the date of the n-th occurrence of `weekday` in `month`/`year`.

    `weekday` follows datetime convention: Monday=0 ... Sunday=6.
    """
    d = _dt.date(year, month, 1)
    first_weekday = d.weekday()
    offset = (weekday - first_weekday) % 7
    day = 1 + offset + 7 * (n - 1)
    return _dt.date(year, month, day)


def _last_weekday_of_month(year: int, month: int, weekday: int) -> _dt.date:
    if month == 12:
        next_month_first = _dt.date(year + 1, 1, 1)
    else:
        next_month_first = _dt.date(year, month + 1, 1)
    d = next_month_first - _dt.timedelta(days=1)
    while d.weekday() != weekday:
        d -= _dt.timedelta(days=1)
    return d


def _observed(date: _dt.date) -> _dt.date:
    """Shift a fixed-date federal holiday per 5 U.S.C. S 6103(b)."""
    if date.weekday() == 5:  # Saturday -> observed Friday
        return date - _dt.timedelta(days=1)
    if date.weekday() == 6:  # Sunday -> observed Monday
        return date + _dt.timedelta(days=1)
    return date


def federal_holidays(year: int) -> set:
    """Legal holidays under 5 U.S.C. S 6103, as incorporated by Fed. R. Civ. P. 6(a)(6)(A)."""
    fixed = [
        _dt.date(year, 1, 1),    # New Year's Day
        _dt.date(year, 6, 19),   # Juneteenth National Independence Day
        _dt.date(year, 7, 4),    # Independence Day
        _dt.date(year, 11, 11),  # Veterans Day
        _dt.date(year, 12, 25),  # Christmas Day
    ]
    holidays = {_observed(d) for d in fixed}
    holidays.add(_nth_weekday_of_month(year, 1, 0, 3))   # MLK Day, 3rd Monday Jan
    holidays.add(_nth_weekday_of_month(year, 2, 0, 3))   # Washington's Birthday, 3rd Monday Feb
    holidays.add(_last_weekday_of_month(year, 5, 0))     # Memorial Day, last Monday May
    holidays.add(_nth_weekday_of_month(year, 9, 0, 1))   # Labor Day, 1st Monday Sept
    holidays.add(_nth_weekday_of_month(year, 10, 0, 2))  # Columbus Day, 2nd Monday Oct
    holidays.add(_nth_weekday_of_month(year, 11, 3, 4))  # Thanksgiving, 4th Thursday Nov
    return holidays


def florida_holidays(year: int) -> set:
    """Legal holidays under Fla. Stat. S 683.01, as incorporated by Fla. R. Jud. Admin. 2.514(a)(6)."""
    holidays = {
        _dt.date(year, 1, 1),    # New Year's Day
    }
    holidays.add(_nth_weekday_of_month(year, 1, 0, 3))   # Birthday of MLK Jr.
    holidays.add(_dt.date(year, 6, 19))                  # Juneteenth
    holidays.add(_dt.date(year, 7, 4))                   # Independence Day
    holidays.add(_nth_weekday_of_month(year, 9, 0, 1))   # Labor Day
    holidays.add(_dt.date(year, 11, 11))                 # Veterans Day
    holidays.add(_nth_weekday_of_month(year, 11, 3, 4))  # Thanksgiving
    holidays.add(_nth_weekday_of_month(year, 11, 3, 4) + _dt.timedelta(days=1))  # Friday after Thanksgiving
    holidays.add(_dt.date(year, 12, 25))                 # Christmas Day
    return holidays


HOLIDAY_SETS = {
    "federal": federal_holidays,
    "florida": florida_holidays,
}
