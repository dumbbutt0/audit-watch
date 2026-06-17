#!/usr/bin/env python3
"""
next_skill_reminder.py — Stop hook: when the pipeline is parked at a skill-pending pause,
remind which in-session /skill (or resume subcommand) comes next, so the api-free flow doesn't
stall waiting on a step the operator forgot. Stays SILENT unless a skill is actually pending.

Contract: Stop hooks run when the assistant finishes a turn. Always exit 0 (informational);
prints a one-line reminder to stderr only when a pause is detected. Never blocks.

Manually runnable:  python scripts/hooks/next_skill_reminder.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _hooklib as hooklib  # noqa: E402


def _session_step() -> str:
    p = hooklib.audit_file("session.json")
    if p is None or not p.exists():
        return ""
    try:
        return str(json.loads(p.read_text()).get("active_step", ""))
    except (json.JSONDecodeError, OSError):
        return ""


def _exists(*parts: str) -> bool:
    p = hooklib.audit_file(*parts)
    return bool(p and p.exists())


def _pending_reminder() -> str | None:
    # Step 0: deep-analysis bundle prepared but artifacts not yet validated/written.
    if _exists("data", "invariants", "_bundles", "index.json") and \
       not _exists("data", "invariants", "_deep_analysis_complete.json") and \
       not _exists("data", "invariants", "protocol_invariants.json"):
        return ("Step 0 pending → run the /deep-analysis skill, then "
                "`./run_pipeline.sh analyze-resume`.")

    # Step 4: triage bundles prepared but decisions not yet produced.
    if _exists("data", "triage", "_bundles", "index.json") and \
       not _exists("data", "triage", "_decisions.json"):
        return ("Step 4 pending → run the /triage skill, then "
                "`python scripts/triage_write.py` and `./run_pipeline.sh review-gate`.")

    return None


def main() -> int:
    hooklib.read_hook_input()  # consume payload (unused); keeps us a well-behaved Stop hook
    if not hooklib.active_audit_id():
        return hooklib.ALLOW
    reminder = _pending_reminder()
    if reminder:
        print(f"[audit-watch] Next: {reminder}", file=sys.stderr)
    return hooklib.ALLOW


if __name__ == "__main__":
    sys.exit(main())
