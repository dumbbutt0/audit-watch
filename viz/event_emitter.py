"""
viz/event_emitter.py — Zero-friction event emitter for the reasoning visualization layer.

Usage in any pipeline script (one line, no refactor needed):

    from viz.event_emitter import emit

    emit("HYPOTHESIS_BORN", source_agent="reentrancy_agent", payload={
        "hypothesis_text": "Collateral desync via reentrancy in withdraw()",
        "linked_contracts": ["LendingPool.sol"],
        "severity_ceiling": "CRITICAL",
        "confidence": 0.6,
        "exploit_class": "reentrancy",
    })

The emitter:
- Never blocks the calling agent (fire-and-forget)
- Gracefully degrades if VIZ_SESSION_ID is not set (silent skip)
- Writes to data/sessions/{session_id}/events.jsonl (atomic append)
- Thread-safe: uses a per-session-file lock
- All I/O wrapped in try/except — never raises, logs warning at most
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_FILE_LOCKS: dict[str, threading.Lock] = {}
_LOCKS_LOCK = threading.Lock()


def _get_lock(path: str) -> threading.Lock:
    with _LOCKS_LOCK:
        if path not in _FILE_LOCKS:
            _FILE_LOCKS[path] = threading.Lock()
        return _FILE_LOCKS[path]


def emit(
    event_type: str,
    source_agent: str = "unknown",
    target_node_id: str | None = None,
    payload: dict | None = None,
) -> None:
    """
    Emit a visualization event. Fire-and-forget — never raises.

    Args:
        event_type:     One of the VizEvent event_type enum values.
        source_agent:   Name of the calling script/agent.
        target_node_id: Graph node ID this event affects. If None, auto-generated
                        from payload.id or a fresh UUID prefix.
        payload:        Event-specific data dict.
    """
    try:
        session_id = os.environ.get("VIZ_SESSION_ID", "").strip()
        if not session_id:
            return  # viz not active — silent skip

        events_file = _ROOT / "data" / "sessions" / session_id / "events.jsonl"
        if not events_file.parent.exists():
            return  # session dir not created yet — silent skip

        # Resolve target_node_id
        if target_node_id is None and payload:
            # Try to pull an ID from common payload fields
            for key in ("finding_id", "id", "thread_id", "invariant_id"):
                if key in payload and payload[key]:
                    target_node_id = str(payload[key])
                    break

        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_agent": source_agent,
            "target_node_id": target_node_id,
            "audit_session_id": session_id,
            "payload": payload or {},
        }

        line = json.dumps(event, separators=(",", ":")) + "\n"

        lock = _get_lock(str(events_file))
        with lock:
            with events_file.open("a", encoding="utf-8") as fh:
                fh.write(line)

        # Intercept gate: hold event if a breakpoint fires
        if os.environ.get("VIZ_INTERCEPT", "1") != "0":
            try:
                from viz.intercept.gate import check_gate
                event = check_gate(event, session_id)
            except Exception:
                pass  # never block pipeline on viz errors

    except Exception:
        pass  # viz layer NEVER crashes the pipeline
