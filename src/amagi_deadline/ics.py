"""Minimal .ics (iCalendar, RFC 5545) writer for computed deadlines.

Deliberately dependency-free: writes a VCALENDAR with one all-day VEVENT
per deadline. Good enough to import into Outlook/Google/Apple Calendar;
not a general-purpose iCalendar library.
"""

from __future__ import annotations

import datetime as _dt
from typing import Iterable

from .engine import DeadlineResult

_CRLF = "\r\n"


def _escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def _fold(line: str) -> str:
    """Fold a line to 75 octets per RFC 5545 S 3.1, with CRLF + single-space continuation."""
    if len(line) <= 75:
        return line
    parts = []
    while len(line) > 75:
        parts.append(line[:75])
        line = line[75:]
    parts.append(line)
    return (_CRLF + " ").join(parts)


def build_ics(results: Iterable[DeadlineResult], calendar_name: str = "amagi-deadline") -> str:
    now = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AmagiLabs (Amagisolutionsgroup, Inc.)//amagi-deadline//EN",
        "CALSCALE:GREGORIAN",
        f"X-WR-CALNAME:{_escape(calendar_name)}",
    ]
    for idx, result in enumerate(results):
        dtstart = result.deadline_date.strftime("%Y%m%d")
        dtend = (result.deadline_date + _dt.timedelta(days=1)).strftime("%Y%m%d")
        uid = f"{dtstart}-{idx}-{result.event.key}@amagi-deadline"
        summary = f"DEADLINE: {result.event.label} ({result.rule_set.id})"
        description = (
            f"Rule: {result.event.cite}. Counting rule: {result.rule_set.counting_rule_cite}. "
            f"Trigger date: {result.trigger_date.isoformat()}. "
            "NOT LEGAL ADVICE -- verify against the court's current rules before relying on this date."
        )
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{now}",
                f"DTSTART;VALUE=DATE:{dtstart}",
                f"DTEND;VALUE=DATE:{dtend}",
                _fold(f"SUMMARY:{_escape(summary)}"),
                _fold(f"DESCRIPTION:{_escape(description)}"),
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    return _CRLF.join(lines) + _CRLF


def write_ics(results: Iterable[DeadlineResult], path: str, calendar_name: str = "amagi-deadline") -> None:
    content = build_ics(results, calendar_name=calendar_name)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(content)
