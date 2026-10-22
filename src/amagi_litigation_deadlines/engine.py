"""Deadline computation engine.

Implements the shared day-counting algorithm used by both bundled rule
sets (Fed. R. Civ. P. 6(a) and Fla. R. Jud. Admin. 2.514(a)):

1. Exclude the day of the triggering event.
2. Count every day, including intermediate Saturdays, Sundays, and legal
   holidays.
3. Include the last day of the period, but if that day is a Saturday,
   Sunday, or legal holiday, roll forward to the next day that is none
   of those.

This module does NOT know about any specific court's local closures,
standing orders, or any rule's exceptions (e.g. shorter electronic-service
add-on periods were eliminated by the 2016 FRCP amendments, but a given
local rule could still vary a period). It is a calculator for the
general rule only -- see the README and SKILL disclaimers.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass

from . import holidays as _holidays
from .rules import Event, RuleSet


@dataclass(frozen=True)
class DeadlineResult:
    event: Event
    rule_set: RuleSet
    trigger_date: _dt.date
    raw_date: _dt.date
    deadline_date: _dt.date
    rolled_forward: bool


def _is_holiday(date: _dt.date, holiday_fn) -> bool:
    return date in holiday_fn(date.year)


def _is_weekend(date: _dt.date) -> bool:
    return date.weekday() >= 5  # Saturday=5, Sunday=6


def roll_forward(date: _dt.date, holiday_fn) -> _dt.date:
    """Advance `date` until it is not a weekend day or legal holiday."""
    while _is_weekend(date) or _is_holiday(date, holiday_fn):
        date += _dt.timedelta(days=1)
    return date


def compute_deadline(rule_set: RuleSet, event: Event, trigger_date: _dt.date) -> DeadlineResult:
    """Compute the deadline for `event` under `rule_set`, starting from `trigger_date`.

    `trigger_date` is excluded from the count (per Rule 6(a)(1)(A) / Fla.
    R. Jud. Admin. 2.514(a)(1)), so the raw (pre-rollforward) deadline is
    simply `trigger_date + event.days` days.
    """
    try:
        holiday_fn = _holidays.HOLIDAY_SETS[rule_set.holiday_set]
    except KeyError as exc:
        raise ValueError(f"Unknown holiday set '{rule_set.holiday_set}'") from exc

    raw_date = trigger_date + _dt.timedelta(days=event.days)
    deadline_date = roll_forward(raw_date, holiday_fn)
    return DeadlineResult(
        event=event,
        rule_set=rule_set,
        trigger_date=trigger_date,
        raw_date=raw_date,
        deadline_date=deadline_date,
        rolled_forward=(deadline_date != raw_date),
    )
