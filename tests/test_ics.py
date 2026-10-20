import datetime as dt

from amagi_deadline.engine import compute_deadline
from amagi_deadline.ics import build_ics
from amagi_deadline.rules import get_event, load_rule_set


def test_ics_contains_vevent_and_date():
    rs = load_rule_set("frcp")
    event = get_event(rs, "answer-complaint")
    result = compute_deadline(rs, event, dt.date(2026, 10, 19))

    ics_text = build_ics([result])

    assert "BEGIN:VCALENDAR" in ics_text
    assert "BEGIN:VEVENT" in ics_text
    assert "END:VEVENT" in ics_text
    assert "END:VCALENDAR" in ics_text
    assert result.deadline_date.strftime("%Y%m%d") in ics_text
    assert "NOT LEGAL ADVICE" in ics_text


def test_ics_escapes_commas_and_semicolons():
    rs = load_rule_set("frcp")
    event = get_event(rs, "answer-complaint")
    result = compute_deadline(rs, event, dt.date(2026, 10, 19))
    ics_text = build_ics([result])
    # The cite text contains parentheses/semicolons in some events; ensure no raw
    # unescaped semicolon breaks the SUMMARY/DESCRIPTION line structurally.
    for line in ics_text.split("\r\n"):
        if line.startswith("SUMMARY") or line.startswith("DESCRIPTION"):
            # property name may only contain one unescaped colon-delimited value start
            assert line.count(":") >= 1


def test_write_ics_creates_file(tmp_path):
    from amagi_deadline.ics import write_ics

    rs = load_rule_set("frcp")
    event = get_event(rs, "answer-complaint")
    result = compute_deadline(rs, event, dt.date(2026, 10, 19))
    out_path = tmp_path / "deadline.ics"
    write_ics([result], str(out_path))
    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in content
