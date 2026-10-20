"""Loading and lookup of the bundled YAML rule sets."""

from __future__ import annotations

import importlib.resources as resources
from dataclasses import dataclass
from typing import Dict

import yaml


class RuleError(KeyError):
    """Raised when a rule set or event name is not found."""


@dataclass(frozen=True)
class Event:
    key: str
    label: str
    days: int
    cite: str


@dataclass(frozen=True)
class RuleSet:
    id: str
    name: str
    counting_rule_cite: str
    holiday_set: str
    source_note: str
    events: Dict[str, Event]


_BUNDLED = ("frcp", "florida")


def _load_yaml_text(rule_set_id: str) -> str:
    package_data = resources.files("amagi_deadline") / "data" / f"{rule_set_id}.yaml"
    try:
        return package_data.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuleError(
            f"Unknown rule set '{rule_set_id}'. Available: {', '.join(_BUNDLED)}"
        ) from exc


def load_rule_set(rule_set_id: str) -> RuleSet:
    """Load a bundled rule set by id (e.g. 'frcp', 'florida')."""
    raw = yaml.safe_load(_load_yaml_text(rule_set_id))
    events = {
        key: Event(key=key, label=val["label"], days=int(val["days"]), cite=val["cite"])
        for key, val in raw["events"].items()
    }
    return RuleSet(
        id=raw["id"],
        name=raw["name"],
        counting_rule_cite=raw["counting_rule_cite"],
        holiday_set=raw["holiday_set"],
        source_note=raw.get("source_note", "").strip(),
        events=events,
    )


def available_rule_sets():
    return list(_BUNDLED)


def get_event(rule_set: RuleSet, event_key: str) -> Event:
    try:
        return rule_set.events[event_key]
    except KeyError as exc:
        available = ", ".join(sorted(rule_set.events))
        raise RuleError(
            f"Unknown event '{event_key}' for rule set '{rule_set.id}'. "
            f"Available events: {available}"
        ) from exc
