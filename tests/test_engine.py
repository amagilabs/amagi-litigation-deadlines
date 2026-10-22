import datetime as dt

import pytest

from amagi_litigation_deadlines.engine import compute_deadline
from amagi_litigation_deadlines.rules import get_event, load_rule_set


@pytest.fixture
def frcp():
    return load_rule_set("frcp")


@pytest.fixture
def florida():
    return load_rule_set("florida")


def test_answer_complaint_plain_21_days_no_rollforward(frcp):
    # 2026-10-19 (Monday) + 21 days = 2026-11-09 (Monday) -- no weekend/holiday landing.
    event = get_event(frcp, "answer-complaint")
    result = compute_deadline(frcp, event, dt.date(2026, 10, 19))
    assert result.deadline_date == dt.date(2026, 11, 9)
    assert result.rolled_forward is False


def test_rolls_forward_off_a_saturday():
    frcp = load_rule_set("frcp")
    event = get_event(frcp, "reply-to-counterclaim")
    # Pick a Friday trigger so start + 21 days lands on a Saturday.
    # 2026-10-23 is a Friday; +21 days = 2026-11-13 (Friday) -- adjust to find a Sat landing.
    # Use a trigger where day 21 lands on Saturday: trigger on a Friday where
    # Friday + 21 = Friday + 3 weeks = Friday (same weekday). Need offset of 1 day.
    trigger = dt.date(2026, 10, 24)  # Saturday
    result = compute_deadline(frcp, event, trigger)
    raw = trigger + dt.timedelta(days=21)
    assert raw.weekday() == 5  # confirm the raw date really is a Saturday
    assert result.raw_date == raw
    assert result.rolled_forward is True
    assert result.deadline_date.weekday() not in (5, 6)
    assert result.deadline_date > raw


def test_rolls_forward_off_a_legal_holiday(frcp):
    event = get_event(frcp, "answer-complaint")
    # Christmas Day 2026-12-25 is a Friday. Trigger 21 days earlier = 2026-12-04.
    trigger = dt.date(2026, 12, 4)
    result = compute_deadline(frcp, event, trigger)
    assert result.raw_date == dt.date(2026, 12, 25)
    assert result.rolled_forward is True
    assert result.deadline_date == dt.date(2026, 12, 28)  # next Monday


def test_trigger_day_itself_excluded_from_count(frcp):
    event = get_event(frcp, "reply-to-counterclaim")
    trigger = dt.date(2026, 1, 5)  # Monday
    result = compute_deadline(frcp, event, trigger)
    # 21 days later, excluding the trigger day itself, is trigger + 21.
    assert (result.raw_date - trigger).days == 21


def test_florida_answer_complaint_20_days(florida):
    event = get_event(florida, "answer-complaint")
    result = compute_deadline(florida, event, dt.date(2026, 10, 19))
    assert result.raw_date == dt.date(2026, 10, 19) + dt.timedelta(days=20)
    assert event.cite == "Fla. R. Civ. P. 1.140(a)(1)"


def test_unknown_event_raises(frcp):
    from amagi_litigation_deadlines.rules import RuleError

    with pytest.raises(RuleError):
        get_event(frcp, "does-not-exist")


def test_unknown_rule_set_raises():
    from amagi_litigation_deadlines.rules import RuleError

    with pytest.raises(RuleError):
        load_rule_set("not-a-real-rule-set")
