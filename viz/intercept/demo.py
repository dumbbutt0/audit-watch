#!/usr/bin/env python3
"""
viz/intercept/demo.py — Standalone intercept layer demo.

Emits 5 events with 1-second delays. The 3rd event (BRANCH_INVALIDATED)
pauses at the gate if a matching breakpoint is active. Shows fork creation.

Usage:
    # Use an existing session (creates one if not specified):
    python viz/intercept/demo.py

    # Use a specific session:
    python viz/intercept/demo.py --session <session_id>

    # Auto-add a breakpoint on BRANCH_INVALIDATED so the demo pauses:
    python viz/intercept/demo.py --auto-breakpoint

    # Skip the breakpoint (gate won't fire):
    python viz/intercept/demo.py --no-breakpoint
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT))


def _ensure_session(session_id: str | None) -> str:
    if session_id:
        os.environ["VIZ_SESSION_ID"] = session_id
        # Make sure dir exists
        sess_dir = _ROOT / "data" / "sessions" / session_id
        sess_dir.mkdir(parents=True, exist_ok=True)
        events = sess_dir / "events.jsonl"
        if not events.exists():
            events.touch()
        return session_id

    # Try current session
    from viz.session import get_current_session, create_session
    existing = get_current_session()
    if existing:
        os.environ["VIZ_SESSION_ID"] = existing
        return existing

    # Create fresh demo session
    sid = create_session(audit_target="demo-contract.sol", audit_id="demo")
    print(f"  Created new session: {sid}")
    return sid


def main():
    parser = argparse.ArgumentParser(description="Intercept layer demo")
    parser.add_argument("--session", default=None, help="Session ID to use")
    parser.add_argument("--auto-breakpoint", action="store_true",
                        help="Auto-add BRANCH_INVALIDATED breakpoint before demo")
    parser.add_argument("--no-breakpoint", action="store_true",
                        help="Skip breakpoint (demo runs without pausing)")
    args = parser.parse_args()

    os.environ["VIZ_INTERCEPT"] = "1"

    sid = _ensure_session(args.session)
    print(f"\n  Demo session: {sid}")
    print(f"  Viz server:   http://localhost:8766")
    print(f"  Session URL:  http://localhost:8766/?session={sid}")
    print()

    # Optionally add a breakpoint
    if args.auto_breakpoint and not args.no_breakpoint:
        from viz.intercept.breakpoints import add_breakpoint
        bp = add_breakpoint(
            sid,
            conditions=[{"field": "event_type", "operator": "eq", "value": "BRANCH_INVALIDATED"}],
            label="Demo: hold BRANCH_INVALIDATED",
        )
        print(f"  [breakpoint] Added: {bp.id} — event_type = BRANCH_INVALIDATED")
        print(f"  Open http://localhost:8766 to inspect held events.\n")

    from viz.event_emitter import emit

    # Event 1: hypothesis born
    print("  [1/5] Emitting HYPOTHESIS_BORN for DEMO-001…")
    emit("HYPOTHESIS_BORN", source_agent="demo", target_node_id="DEMO-001", payload={
        "hypothesis_text": "Demo: Reentrancy in withdraw()",
        "severity_ceiling": "HIGH",
        "confidence": 0.55,
        "exploit_class": "reentrancy",
        "linked_contracts": ["demo-contract.sol"],
    })
    time.sleep(1)

    # Event 2: KB match
    print("  [2/5] Emitting KB_MATCH for DEMO-001…")
    emit("KB_MATCH", source_agent="retriever", target_node_id="DEMO-001", payload={
        "solodit_id": "KB-DEMO-99",
        "title": "Similar reentrancy finding in DemoVault",
        "similarity_score": 0.82,
        "exploit_pattern": "reentrancy",
        "historical_severity": "High",
    })
    time.sleep(1)

    # Event 3: BRANCH_INVALIDATED — will pause here if breakpoint is active
    print("  [3/5] Emitting BRANCH_INVALIDATED for DEMO-001…", end="", flush=True)
    if not args.no_breakpoint:
        from viz.intercept.breakpoints import load_breakpoints, matches_any_breakpoint
        bps = load_breakpoints(sid)
        if matches_any_breakpoint({"event_type": "BRANCH_INVALIDATED", "payload": {}}, bps):
            print()
            print()
            print("  *** EVENT HELD AT GATE ***")
            print("  Open http://localhost:8766 — pending panel shows 1 held event")
            print("  Click [RELEASE] to continue, [MODIFY] to change reason, [DROP] to discard")
            print()

    emit("BRANCH_INVALIDATED", source_agent="defense_mapper", target_node_id="DEMO-001", payload={
        "reason": "nonReentrant guard detected via ReentrancyGuard inheritance",
        "score": 12,
    })
    print(" done")
    time.sleep(1)

    # Event 4: hypothesis for second finding
    print("  [4/5] Emitting HYPOTHESIS_BORN for DEMO-002…")
    emit("HYPOTHESIS_BORN", source_agent="demo", target_node_id="DEMO-002", payload={
        "hypothesis_text": "Demo: Missing access control on setConfig()",
        "severity_ceiling": "CRITICAL",
        "confidence": 0.7,
        "exploit_class": "access-control",
        "linked_contracts": ["demo-contract.sol"],
    })
    time.sleep(1)

    # Event 5: triage decision
    print("  [5/5] Emitting TRIAGER_DECISION for DEMO-002…")
    emit("TRIAGER_DECISION", source_agent="triage", target_node_id="DEMO-002", payload={
        "decision": "submit",
        "recommended_severity": "Critical",
        "score": 28,
    })

    print()
    print("  All events emitted.")
    print()

    # Create a fork from event index 1 with modified confidence
    print("  Creating fork from event index 1 (KB_MATCH) with confidence → 0.9…")
    try:
        from viz.intercept.fork import Fork
        fork_id = Fork().create_fork(
            source_session_id=sid,
            branch_from_event_index=1,
            fork_label="Demo: confidence boosted to 0.9",
            modification={
                "target_node_id": "DEMO-001",
                "field": "payload.confidence",
                "old_value": 0.55,
                "new_value": 0.9,
            },
        )
        print(f"  Fork created: {fork_id}")
        print(f"  Fork URL: http://localhost:8766/?session={fork_id}&replay=1")
        print(f"  Compare: http://localhost:8766/?session={sid}")
    except Exception as e:
        print(f"  Fork failed (is session dir writable?): {e}")

    print()
    print("  Demo complete. View at http://localhost:8766")
    print()


if __name__ == "__main__":
    main()
