"""
viz/replay.py — Historical session replay logic.

Loads a completed session's events.jsonl and replays them into a GraphState
at any point in time. Used by the frontend's timeline scrubber.
"""

from __future__ import annotations

import json
from pathlib import Path

from viz.graph_state import GraphState
from viz.session import get_events_file


class ReplaySession:
    """
    Loads all events from a completed session and supports point-in-time graph reconstruction.
    """

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self._events: list[dict] = self._load_events()

    def _load_events(self) -> list[dict]:
        events_file = get_events_file(self.session_id)
        if not events_file.exists():
            return []
        events = []
        try:
            for line in events_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        return events

    def event_count(self) -> int:
        return len(self._events)

    def events_up_to(self, event_index: int) -> list[dict]:
        """Return all events from 0 to event_index (inclusive)."""
        return self._events[:max(0, event_index + 1)]

    def graph_at(self, event_index: int) -> dict:
        """
        Replay events 0..event_index and return the graph snapshot at that point.
        """
        state = GraphState()
        for event in self.events_up_to(event_index):
            state.apply_event(event)
        return state.snapshot()

    def all_events(self) -> list[dict]:
        return list(self._events)

    def event_at(self, index: int) -> dict | None:
        if 0 <= index < len(self._events):
            return self._events[index]
        return None
