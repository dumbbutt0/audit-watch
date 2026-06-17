"""
viz/intercept/tests/test_gate.py — Integration tests for the gate mechanism.

Run with:
    pytest viz/intercept/tests/test_gate.py -v
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from pathlib import Path

import pytest

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def session(tmp_path, monkeypatch):
    """Create a temporary session directory and set VIZ_SESSION_ID."""
    sessions_dir = tmp_path / "data" / "sessions"
    sid = "test-sess"
    sess_dir = sessions_dir / sid
    sess_dir.mkdir(parents=True)
    (sess_dir / "events.jsonl").touch()

    # Patch _ROOT inside gate and breakpoints to tmp_path
    import viz.intercept.gate as gate_mod
    import viz.intercept.breakpoints as bp_mod
    monkeypatch.setattr(gate_mod, "_ROOT", tmp_path)
    monkeypatch.setattr(bp_mod, "_ROOT", tmp_path)
    monkeypatch.setenv("VIZ_SESSION_ID", sid)
    monkeypatch.setenv("VIZ_INTERCEPT", "1")
    monkeypatch.setenv("VIZ_GATE_TIMEOUT", "2")  # 2s timeout for tests

    return sid, sess_dir


def _make_event(event_type: str = "BRANCH_INVALIDATED",
                confidence: float = 0.3,
                target_id: str = "XTR-001") -> dict:
    import uuid
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "timestamp": "2026-01-01T00:00:00Z",
        "source_agent": "test",
        "target_node_id": target_id,
        "audit_session_id": "test-sess",
        "payload": {"confidence": confidence, "decision": "rejected"},
    }


def _add_bp(session_id, tmp_path, conditions, match_mode="any"):
    """Helper: write a breakpoints.json to the session dir."""
    import viz.intercept.breakpoints as bp_mod
    bp_mod._ROOT = tmp_path
    from viz.intercept.breakpoints import add_breakpoint
    return add_breakpoint(session_id, conditions, match_mode)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_gate_disabled_when_no_breakpoints(session, tmp_path):
    sid, sess_dir = session
    from viz.intercept.gate import check_gate
    event = _make_event()
    result = check_gate(event, sid)
    assert result is event  # returned original immediately


def test_gate_disabled_when_viz_intercept_0(session, tmp_path, monkeypatch):
    sid, sess_dir = session
    monkeypatch.setenv("VIZ_INTERCEPT", "0")
    # Add a matching breakpoint — gate should still not fire
    _add_bp(sid, tmp_path, [{"field": "event_type", "operator": "eq", "value": "BRANCH_INVALIDATED"}])
    from viz.intercept.gate import check_gate
    event = _make_event("BRANCH_INVALIDATED")
    result = check_gate(event, sid)
    assert result is event


def test_breakpoint_matching_event_type(session, tmp_path):
    sid, sess_dir = session
    _add_bp(sid, tmp_path, [{"field": "event_type", "operator": "eq", "value": "BRANCH_INVALIDATED"}])
    from viz.intercept.breakpoints import load_breakpoints, matches_any_breakpoint
    bps = load_breakpoints(sid)
    assert len(bps) == 1
    assert matches_any_breakpoint(_make_event("BRANCH_INVALIDATED"), bps)
    assert not matches_any_breakpoint(_make_event("HYPOTHESIS_BORN"), bps)


def test_breakpoint_matching_payload_field(session, tmp_path):
    sid, sess_dir = session
    _add_bp(sid, tmp_path, [{"field": "payload.confidence", "operator": "lt", "value": 0.4}])
    from viz.intercept.breakpoints import load_breakpoints, matches_any_breakpoint
    bps = load_breakpoints(sid)
    assert matches_any_breakpoint(_make_event(confidence=0.3), bps)
    assert not matches_any_breakpoint(_make_event(confidence=0.8), bps)


def test_gate_release_via_file_delete(session, tmp_path, monkeypatch):
    sid, sess_dir = session
    _add_bp(sid, tmp_path, [{"field": "event_type", "operator": "eq", "value": "BRANCH_INVALIDATED"}])
    from viz.intercept.gate import check_gate

    event = _make_event("BRANCH_INVALIDATED")
    eid = event["event_id"]
    pending_path = sess_dir / "pending" / f"{eid}.json"

    results = []

    def _run():
        r = check_gate(event, sid)
        results.append(r)

    t = threading.Thread(target=_run)
    t.start()

    # Wait for pending file to appear
    for _ in range(50):
        if pending_path.exists():
            break
        time.sleep(0.05)
    assert pending_path.exists(), "pending file should exist while gate is held"

    # Release: delete the pending file
    pending_path.unlink()
    t.join(timeout=3)
    assert not t.is_alive(), "gate should have released"
    assert results[0] is event  # returned unmodified


def test_gate_modification_via_modified_file(session, tmp_path):
    sid, sess_dir = session
    _add_bp(sid, tmp_path, [{"field": "event_type", "operator": "eq", "value": "BRANCH_INVALIDATED"}])
    from viz.intercept.gate import check_gate

    event = _make_event("BRANCH_INVALIDATED")
    eid = event["event_id"]
    pending_path  = sess_dir / "pending" / f"{eid}.json"
    modified_path = sess_dir / "pending" / f"{eid}.modified.json"

    results = []

    def _run():
        r = check_gate(event, sid)
        results.append(r)

    t = threading.Thread(target=_run)
    t.start()

    for _ in range(50):
        if pending_path.exists():
            break
        time.sleep(0.05)

    # Write modified event
    modified = dict(event)
    modified["payload"] = {**event["payload"], "decision": "submit"}
    modified["_intercept_field_modified"] = "payload.decision"
    modified["_intercept_old_value"] = "rejected"
    modified["_intercept_new_value"] = "submit"
    modified_path.write_text(json.dumps(modified))
    # Delete pending to unblock
    pending_path.unlink()
    t.join(timeout=3)

    assert results[0]["payload"]["decision"] == "submit"
    # Bookkeeping keys stripped
    assert "_intercept_field_modified" not in results[0]


def test_gate_auto_release_on_timeout(session, tmp_path, monkeypatch):
    sid, sess_dir = session
    monkeypatch.setenv("VIZ_GATE_TIMEOUT", "0.4")  # very short timeout
    _add_bp(sid, tmp_path, [{"field": "event_type", "operator": "eq", "value": "BRANCH_INVALIDATED"}])
    from viz.intercept.gate import check_gate

    event = _make_event("BRANCH_INVALIDATED")
    start = time.monotonic()
    result = check_gate(event, sid)
    elapsed = time.monotonic() - start

    assert result is event  # auto-released
    assert elapsed < 3.0, f"should have timed out quickly, took {elapsed:.1f}s"

    # GATE_RELEASED event should be in events.jsonl with timed_out=True
    events_raw = (sess_dir / "events.jsonl").read_text()
    gate_events = [json.loads(l) for l in events_raw.splitlines() if l.strip()]
    released = [e for e in gate_events if e.get("event_type") == "GATE_RELEASED"]
    assert released, "GATE_RELEASED event should be written"
    assert released[-1]["payload"].get("timed_out") is True
