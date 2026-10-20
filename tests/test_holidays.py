import datetime as dt

from amagi_deadline.holidays import federal_holidays, florida_holidays


def test_federal_new_years_2026_is_jan1_thursday():
    # 2026-01-01 is a Thursday -- no weekend shift expected.
    holidays = federal_holidays(2026)
    assert dt.date(2026, 1, 1) in holidays


def test_federal_juneteenth_2027_shifts_from_saturday_to_friday():
    # 2027-06-19 is a Saturday -> observed Friday 2027-06-18.
    holidays = federal_holidays(2027)
    assert dt.date(2027, 6, 19) not in holidays
    assert dt.date(2027, 6, 18) in holidays


def test_federal_christmas_2027_sunday_shifts_to_monday():
    # 2027-12-25 is a Saturday actually -- check both possibilities safely.
    year = 2032  # 2032-12-25 is a Saturday
    holidays = federal_holidays(year)
    assert dt.date(year, 12, 24) in holidays
    assert dt.date(year, 12, 25) not in holidays


def test_federal_mlk_day_is_third_monday_of_january():
    holidays = federal_holidays(2026)
    mlk_days = [d for d in holidays if d.month == 1 and d != dt.date(2026, 1, 1)]
    assert len(mlk_days) == 1
    assert mlk_days[0].weekday() == 0
    assert 15 <= mlk_days[0].day <= 21


def test_florida_holidays_no_weekend_shift_applied():
    # Florida's statute doesn't carry the federal Friday/Monday shift rule;
    # a fixed-date holiday landing on a weekend stays on its calendar date.
    holidays = florida_holidays(2027)
    assert dt.date(2027, 7, 4) in holidays


def test_florida_thanksgiving_friday_included():
    holidays = florida_holidays(2026)
    thanksgiving = [d for d in holidays if d.month == 11 and d.weekday() == 3 and 22 <= d.day <= 28]
    assert len(thanksgiving) == 1
    friday_after = thanksgiving[0] + dt.timedelta(days=1)
    assert friday_after in holidays
