"""
viz/intercept/repeater.py — Event Repeater (Burp Repeater equivalent).

Capture any event from the session history and replay it through the
in-memory GraphState to see what the graph diff would look like —
without modifying the original session.

Optionally apply field modifications before replaying (dry_run or live).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent


def _sessions_dir() -> Path:
    return _ROOT / "data" / "sessions"


class EventRepeater:
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self._capture_history: list[dict] = []

    def _events_file(self) -> Path:
        return _sessions_dir() / self.session_id / "events.jsonl"

    def _load_all_events(self) -> list[dict]:
        path = self._events_file()
        if not path.exists():
            return []
        events = []
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        return events

    def capture_event(self, event_id: str) -> dict:
        """
        Find an event by event_id in the session JSONL.
        Returns the event dict, or {} if not found.
        """
        for event in self._load_all_events():
            if event.get("event_id") == event_id:
                captured = copy.deepcopy(event)
                captured["_captured_at"] = _now()
                self._capture_history.append(captured)
                return captured
        return {}

    def replay_event(
        self,
        event: dict,
        modifications: dict | None = None,
        dry_run: bool = False,
    ) -> dict:
        """
        Replay an event through a fresh GraphState (built from current session).
        If modifications provided ({field_path: new_value}), apply them first.
        If dry_run=True, return the diff without persisting.

        Returns {diff, nodes_changed, modified_event}.
        """
        from viz.graph_state import GraphState
        from viz.replay import ReplaySession

        # Apply modifications to a copy
        modified = copy.deepcopy(event)
        if modifications:
            for field_path, new_val in modifications.items():
                _set_field(modified, field_path, new_val)

        if dry_run:
            # Replay against a throwaway state built from full session
            replay = ReplaySession(self.session_id)
            state = GraphState()
            for e in replay.all_events():
                state.apply_event(e)
            diff = state.apply_event(modified)
            return {
                "diff": diff,
                "nodes_changed": diff.get("changed", []) + diff.get("added", []),
                "modified_event": modified,
                "dry_run": True,
            }
        else:
            # Not dry_run: just compute the diff against a throwaway state
            state = GraphState()
            diff = state.apply_event(modified)
            return {
                "diff": diff,
                "nodes_changed": diff.get("changed", []) + diff.get("added", []),
                "modified_event": modified,
                "dry_run": False,
            }

    def get_capture_history(self) -> list[dict]:
        """All events captured for replay in this session instance."""
        return list(self._capture_history)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _set_field(obj: dict, field_path: str, value) -> None:
    """Set a dot-path field in a nested dict (mutates in place)."""
    parts = field_path.split(".")
    for part in parts[:-1]:
        if part not in obj or not isinstance(obj[part], dict):
            obj[part] = {}
        obj = obj[part]
    obj[parts[-1]] = value


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
