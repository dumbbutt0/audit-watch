"""
viz/intercept/breakpoints.py — Breakpoint schema and matching logic.

Breakpoints are stored in data/sessions/{session_id}/breakpoints.json.
Each breakpoint has one or more conditions. An event fires a breakpoint
when conditions match according to match_mode ("any" = OR, "all" = AND).

Supported fields:
    event_type          top-level event field
    target_node_id      top-level event field
    source_agent        top-level event field
    payload.*           dot-path into the payload dict, e.g. "payload.confidence"

Supported operators:
    eq          equal (string or numeric)
    neq         not equal
    lt          less than (numeric)
    gt          greater than (numeric)
    contains    substring / list membership
    matches     regex match (re.search)
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent.parent


def _sessions_dir() -> Path:
    return _ROOT / "data" / "sessions"


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class BreakpointCondition:
    field: str      # e.g. "event_type", "payload.confidence"
    operator: str   # eq | neq | lt | gt | contains | matches
    value: Any

    def to_dict(self) -> dict:
        return {"field": self.field, "operator": self.operator, "value": self.value}

    @classmethod
    def from_dict(cls, d: dict) -> "BreakpointCondition":
        return cls(field=d["field"], operator=d["operator"], value=d["value"])


@dataclass
class Breakpoint:
    id: str
    enabled: bool = True
    conditions: list[BreakpointCondition] = field(default_factory=list)
    match_mode: str = "any"   # "any" (OR) | "all" (AND)
    label: str = ""           # human-readable description

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "enabled": self.enabled,
            "conditions": [c.to_dict() for c in self.conditions],
            "match_mode": self.match_mode,
            "label": self.label,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Breakpoint":
        return cls(
            id=d.get("id", str(uuid.uuid4())[:8]),
            enabled=d.get("enabled", True),
            conditions=[BreakpointCondition.from_dict(c) for c in d.get("conditions", [])],
            match_mode=d.get("match_mode", "any"),
            label=d.get("label", ""),
        )


# ── Storage ───────────────────────────────────────────────────────────────────

def _bp_path(session_id: str) -> Path:
    return _sessions_dir() / session_id / "breakpoints.json"


def load_breakpoints(session_id: str) -> list[Breakpoint]:
    """Load active breakpoints from disk. Returns [] if file missing or corrupt."""
    path = _bp_path(session_id)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [Breakpoint.from_dict(b) for b in data if isinstance(b, dict)]
    except Exception:
        return []


def save_breakpoints(session_id: str, breakpoints: list[Breakpoint]) -> None:
    """Persist breakpoints to disk atomically."""
    path = _bp_path(session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps([b.to_dict() for b in breakpoints], indent=2))
    tmp.replace(path)


def add_breakpoint(session_id: str, conditions: list[dict],
                   match_mode: str = "any", label: str = "") -> Breakpoint:
    """Create and persist a new breakpoint. Returns the new Breakpoint."""
    bps = load_breakpoints(session_id)
    bp = Breakpoint(
        id=str(uuid.uuid4())[:8],
        enabled=True,
        conditions=[BreakpointCondition.from_dict(c) for c in conditions],
        match_mode=match_mode,
        label=label,
    )
    bps.append(bp)
    save_breakpoints(session_id, bps)
    return bp


def update_breakpoint(session_id: str, bp_id: str, patch: dict) -> bool:
    """Update fields on a breakpoint. Returns True if found."""
    bps = load_breakpoints(session_id)
    for bp in bps:
        if bp.id == bp_id:
            if "enabled" in patch:
                bp.enabled = bool(patch["enabled"])
            if "conditions" in patch:
                bp.conditions = [BreakpointCondition.from_dict(c)
                                  for c in patch["conditions"]]
            if "match_mode" in patch:
                bp.match_mode = patch["match_mode"]
            if "label" in patch:
                bp.label = patch["label"]
            save_breakpoints(session_id, bps)
            return True
    return False


def delete_breakpoint(session_id: str, bp_id: str) -> bool:
    """Delete a breakpoint by ID. Returns True if found."""
    bps = load_breakpoints(session_id)
    new_bps = [b for b in bps if b.id != bp_id]
    if len(new_bps) == len(bps):
        return False
    save_breakpoints(session_id, new_bps)
    return True


# ── Field access ──────────────────────────────────────────────────────────────

def _get_field(event: dict, field_path: str) -> Any:
    """
    Resolve a dot-path field from an event dict.
    "event_type"              → event["event_type"]
    "payload.confidence"      → event["payload"]["confidence"]
    "payload.decision"        → event["payload"]["decision"]
    """
    parts = field_path.split(".")
    obj: Any = event
    for part in parts:
        if isinstance(obj, dict):
            obj = obj.get(part)
        else:
            return None
    return obj


# ── Condition matching ────────────────────────────────────────────────────────

def _condition_matches(event: dict, cond: BreakpointCondition) -> bool:
    actual = _get_field(event, cond.field)
    expected = cond.value

    try:
        op = cond.operator
        if op == "eq":
            return str(actual).lower() == str(expected).lower()
        elif op == "neq":
            return str(actual).lower() != str(expected).lower()
        elif op == "lt":
            return float(actual) < float(expected)
        elif op == "gt":
            return float(actual) > float(expected)
        elif op == "contains":
            if isinstance(actual, list):
                return expected in actual
            return str(expected).lower() in str(actual).lower()
        elif op == "matches":
            return bool(re.search(str(expected), str(actual or "")))
    except Exception:
        pass
    return False


def _breakpoint_fires(event: dict, bp: Breakpoint) -> bool:
    if not bp.enabled or not bp.conditions:
        return False
    results = [_condition_matches(event, c) for c in bp.conditions]
    if bp.match_mode == "all":
        return all(results)
    return any(results)  # "any" = OR (default)


# ── Public matching API ───────────────────────────────────────────────────────

def matches_any_breakpoint(event: dict, breakpoints: list[Breakpoint]) -> bool:
    return any(_breakpoint_fires(event, bp) for bp in breakpoints)


def get_matching_breakpoint(event: dict, breakpoints: list[Breakpoint]) -> Breakpoint | None:
    for bp in breakpoints:
        if _breakpoint_fires(event, bp):
            return bp
    return None
