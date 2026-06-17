"""
viz/intercept/gate.py — File-based intercept gate for the reasoning pipeline.

When a breakpoint fires on a VizEvent, check_gate() writes the event to
pending/{event_id}.json and blocks until:
  - The pending file is deleted → released unmodified
  - A .modified.json file appears → apply modification and release
  - Timeout (VIZ_GATE_TIMEOUT seconds, default 300) → auto-release

This is the only IPC mechanism between 24+ independent pipeline scripts.
All coordination happens through the filesystem — no shared process, no broker.

Never raises — all errors return the original event immediately so the
pipeline continues.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_TIMEOUT = 300
_POLL_INTERVAL = 0.2


def _sessions_dir() -> Path:
    return _ROOT / "data" / "sessions"


def _session_dir(session_id: str) -> Path:
    return _sessions_dir() / session_id


def _write_gate_event(event_type: str, related_event: dict,
                      session_id: str, extra: dict | None = None) -> None:
    """Append a GATE_* synthetic event to events.jsonl for the audit trail."""
    try:
        events_file = _session_dir(session_id) / "events.jsonl"
        gate_event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_agent": "intercept_gate",
            "target_node_id": related_event.get("target_node_id"),
            "audit_session_id": session_id,
            "payload": {
                "held_event_id": related_event.get("event_id"),
                **(extra or {}),
            },
        }
        with events_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(gate_event, separators=(",", ":")) + "\n")
    except Exception:
        pass


def check_gate(event: dict, session_id: str) -> dict:
    """
    If a breakpoint fires for this event, hold it in pending/ and block
    until released or modified by the UI.

    Returns the event (possibly with modified payload). Never raises.
    """
    try:
        # Guard: intercept disabled globally
        if os.environ.get("VIZ_INTERCEPT", "1") == "0":
            return event

        if not session_id:
            return event

        from viz.intercept.breakpoints import get_matching_breakpoint, load_breakpoints
        bps = load_breakpoints(session_id)
        if not bps:
            return event  # fast path — no breakpoints configured

        matching_bp = get_matching_breakpoint(event, bps)
        if not matching_bp:
            return event  # no breakpoint fires

        # ── Gate is open — hold the event ────────────────────────────────
        session_path = _session_dir(session_id)
        pending_dir = session_path / "pending"
        held_dir    = session_path / "held"
        pending_dir.mkdir(exist_ok=True)
        held_dir.mkdir(exist_ok=True)

        event_id = event.get("event_id", str(uuid.uuid4()))
        pending_path  = pending_dir / f"{event_id}.json"
        modified_path = pending_dir / f"{event_id}.modified.json"

        # Write pending file
        pending_path.write_text(json.dumps(event, indent=2))

        # Notify audit trail
        _write_gate_event("GATE_OPENED", event, session_id, {
            "matching_breakpoint_id": matching_bp.id,
            "held_at": datetime.now(timezone.utc).isoformat(),
        })

        timeout = float(os.environ.get("VIZ_GATE_TIMEOUT", _DEFAULT_TIMEOUT))
        waited = 0.0
        held_at = time.monotonic()

        # Block: poll until pending file disappears or timeout
        while pending_path.exists() and waited < timeout:
            time.sleep(_POLL_INTERVAL)
            waited += _POLL_INTERVAL

        held_duration = time.monotonic() - held_at

        # Check for human modification
        if modified_path.exists():
            try:
                modified_event = json.loads(modified_path.read_text())
                modified_path.unlink(missing_ok=True)

                # Audit trail
                held_path = held_dir / f"{event_id}.json"
                held_path.write_text(json.dumps({
                    "original": event,
                    "modified": modified_event,
                    "modified_at": datetime.now(timezone.utc).isoformat(),
                    "held_duration_seconds": round(held_duration, 2),
                }, indent=2))

                _write_gate_event("GATE_MODIFIED", event, session_id, {
                    "field_modified": modified_event.get("_intercept_field_modified", ""),
                    "old_value": modified_event.get("_intercept_old_value"),
                    "new_value": modified_event.get("_intercept_new_value"),
                    "released_at": datetime.now(timezone.utc).isoformat(),
                    "held_duration_seconds": round(held_duration, 2),
                })

                # Strip internal intercept bookkeeping keys from the event
                for k in ("_intercept_field_modified", "_intercept_old_value",
                          "_intercept_new_value"):
                    modified_event.pop(k, None)

                return modified_event
            except Exception:
                pass

        # Released unmodified (or timeout)
        _write_gate_event("GATE_RELEASED", event, session_id, {
            "released_at": datetime.now(timezone.utc).isoformat(),
            "held_duration_seconds": round(held_duration, 2),
            "timed_out": waited >= timeout,
        })
        return event

    except Exception:
        return event  # never crash the pipeline
