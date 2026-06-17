#!/usr/bin/env python3
"""
bridge_thread_disposition_write.py — validate + write concrete invalidations for bridge threads the
synthesis/triage skill chose NOT to escalate. Reads data/threads/_bridge_thread_decisions.json
({"dispositions":[{thread_id, exact_sink, attacker_entrypoint, resolution{type,reason}}]}), validates each
against bridge_thread_escalation_gate's contract (no vague labels), and writes the canonical
data/threads/_bridge_thread_dispositions.json. Rejects vague/incomplete records (they stay un-recorded so
the gate keeps blocking — no silent drop). See documentation/bridge_lifecycle_escalation_policy.md.

Usage: python scripts/bridge_thread_disposition_write.py [--decisions <path>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import bridge_thread_escalation_gate as gate  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decisions")
    args = ap.parse_args()
    dec_path = Path(args.decisions) if args.decisions else (audit_path("data/threads") / "_bridge_thread_decisions.json")
    if not dec_path.exists():
        raise SystemExit(f"[bridge_thread_disposition_write] decisions not found: {dec_path}")
    decisions = json.loads(dec_path.read_text())
    if isinstance(decisions, dict):
        decisions = decisions.get("dispositions", [])

    accepted, rejected = [], []
    for d in decisions:
        valid, why = gate._valid_invalidation(d)
        if valid and d.get("thread_id"):
            accepted.append(d)
        else:
            rejected.append({"thread_id": d.get("thread_id", "?"), "_reject": why})

    out = audit_path("data/threads") / "_bridge_thread_dispositions.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"dispositions": accepted}, indent=2))
    print(f"[ok] bridge thread dispositions: {len(accepted)} accepted · {len(rejected)} rejected (kept blocking)")
    for r in rejected:
        print(f"   REJECT {r['thread_id']}: {r['_reject']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
