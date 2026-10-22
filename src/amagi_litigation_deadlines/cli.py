"""Command-line interface for amagi-litigation-deadlines."""

from __future__ import annotations

import argparse
import datetime as _dt
import sys
from typing import List, Optional

from . import __version__
from .engine import DeadlineResult, compute_deadline
from .ics import write_ics
from .rules import RuleError, available_rule_sets, get_event, load_rule_set

DISCLAIMER = (
    "This is not legal advice. amagi-litigation-deadlines computes dates from a "
    "code-maintained summary of court rules. Every computed deadline must "
    "be verified by an attorney against the court's current rules, local "
    "rules, standing orders, and any case-specific order before you rely "
    "on it."
)


def _parse_date(value: str) -> _dt.date:
    try:
        return _dt.date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{value}', expected YYYY-MM-DD"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="amagi-litigation-deadlines",
        description=(
            "Compute litigation response deadlines from a trigger event and date. "
            + DISCLAIMER
        ),
    )
    parser.add_argument("--version", action="version", version=f"amagi-litigation-deadlines {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    list_rules_p = sub.add_parser("list-rule-sets", help="List bundled rule sets.")
    list_rules_p.set_defaults(func=_cmd_list_rule_sets)

    list_events_p = sub.add_parser("list-events", help="List events for a rule set.")
    list_events_p.add_argument("--rules", required=True, choices=available_rule_sets())
    list_events_p.set_defaults(func=_cmd_list_events)

    calc_p = sub.add_parser("calc", help="Compute a deadline for one event.")
    calc_p.add_argument("--rules", required=True, choices=available_rule_sets(), help="Rule set id.")
    calc_p.add_argument("--event", required=True, help="Event key (see list-events).")
    calc_p.add_argument("--date", required=True, type=_parse_date, help="Trigger date, YYYY-MM-DD.")
    calc_p.add_argument("--jurisdiction", default=None, help="Free-text note, e.g. 'M.D. Fla.' (display only).")
    calc_p.add_argument("--ics", default=None, help="If given, also write an .ics file to this path.")
    calc_p.set_defaults(func=_cmd_calc)

    return parser


def _cmd_list_rule_sets(args: argparse.Namespace) -> int:
    for rs_id in available_rule_sets():
        rs = load_rule_set(rs_id)
        print(f"{rs.id:10s} {rs.name} (counting rule: {rs.counting_rule_cite})")
    return 0


def _cmd_list_events(args: argparse.Namespace) -> int:
    rs = load_rule_set(args.rules)
    for key in sorted(rs.events):
        event = rs.events[key]
        print(f"{key:30s} {event.days:3d} day(s)  {event.cite}  -- {event.label}")
    return 0


def _format_table(results: List[DeadlineResult]) -> str:
    lines = [
        "| Event | Trigger date | Deadline | Rolled forward? | Rule cite | Counting rule |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            "| {label} | {trigger} | {deadline} | {rolled} | {cite} | {counting} |".format(
                label=r.event.label,
                trigger=r.trigger_date.isoformat(),
                deadline=r.deadline_date.isoformat(),
                rolled="yes" if r.rolled_forward else "no",
                cite=r.event.cite,
                counting=r.rule_set.counting_rule_cite,
            )
        )
    return "\n".join(lines)


def _cmd_calc(args: argparse.Namespace) -> int:
    try:
        rule_set = load_rule_set(args.rules)
        event = get_event(rule_set, args.event)
    except RuleError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = compute_deadline(rule_set, event, args.date)

    print(f"NOT LEGAL ADVICE: {DISCLAIMER}\n")
    if args.jurisdiction:
        print(f"Jurisdiction (informational only, not used in the calculation): {args.jurisdiction}\n")
    print(_format_table([result]))
    if rule_set.source_note:
        print(f"\nSource rule set note: {rule_set.source_note}")

    if args.ics:
        write_ics([result], args.ics)
        print(f"\nWrote {args.ics}")

    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
