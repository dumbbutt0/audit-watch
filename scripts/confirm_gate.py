#!/usr/bin/env python3
"""
confirm_gate.py — Reachability-truth gate (deterministic, no LLM).

Reads output/confirm/reachability_analysis.json and either WARNS (eval mode) or HARD-FAILS (submission mode)
on candidates whose reachability is not attacker-credible. Additive to the existing gates — does NOT weaken
or replace min_confirm_gate (field presence) / coverage_completeness_gate. NEVER blocks the eval candidate
set: eval mode always exits 0.

  --mode eval        (default) classify + warn only; exit 0 (never blocks the eval candidate set).
  --mode submission  HARD-FAIL (exit 1) if any High/Critical candidate is non-credible (see FAIL_STATUSES).
  --strict           extend the fail set to Medium severity and the `uncertain` status.

Override: AUDITWATCH_CONFIRM_OVERRIDE=1 forces exit 0 even in submission mode.
Writes output/confirm/confirm_gate.json.

Usage: python scripts/confirm_gate.py [--mode eval|submission] [--strict] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

# Statuses that make a finding NOT attacker-credible -> submission-mode HARD-FAIL for High/Critical.
# NOTE: lifecycle_only is deliberately NOT a default hard-fail. In a migration/reseed protocol the CORE
# bugs (e.g. PC-001 global-stalk-not-initialized, a real High HIT) live in reseed/init files and would be
# mislabeled lifecycle_only — auto-killing them would be overclaiming. lifecycle_only therefore routes to
# manual review (warning) in normal submission mode, and only hard-fails under --strict (with an explicit
# accepted-impact decision required from the reviewer).
FAIL_STATUSES = {"external_entrypoint_missing", "privileged_only", "dead_path", "insufficient_evidence"}
LIFECYCLE_FAIL = "lifecycle_only"  # strict-only fail
WARN_STATUSES = {"uncertain", "needs_runtime_poc", "lifecycle_only", "duplicate"}
HIGH = {"high", "critical"}
MED = {"medium"}


def _sev(s: str) -> str:
    return (s or "").split(".")[0].split()[0].lower() if s else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["eval", "submission"], default="eval")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    p = audit_path("output") / "confirm" / "reachability_analysis.json"
    if not p.exists():
        raise SystemExit("[confirm_gate] reachability_analysis.json missing — run confirm_reachability.py first.")
    results = json.loads(p.read_text()).get("results", [])

    fail_statuses = set(FAIL_STATUSES)
    if args.strict:
        fail_statuses |= {LIFECYCLE_FAIL, "uncertain"}  # strict also fails lifecycle_only + uncertain
    fail_sevs = set(HIGH) | (MED if args.strict else set())

    # only CONFIRMED claims are subject to the submission hard-fail: merged findings + eval
    # confirmed_eval_finding. partial_eval_finding / real_world_poc_later already self-declare as
    # non-confirmed (the spec WARNs on partial) -> they warn, never hard-fail.
    inv = {c["finding_id"]: c for c in
           json.loads((audit_path("output") / "confirm" / "confirm_inventory.json").read_text()).get("candidates", [])}

    def _is_confirmed_claim(fid):
        c = inv.get(fid, {})
        return c.get("layer") == "merged" or c.get("classification") == "confirmed_eval_finding"

    blocking, warning = [], []
    for r in results:
        st = r.get("reachability_status")
        sev = _sev(r.get("severity"))
        action = r.get("suggested_action")
        # duplicate is only a fail if not merged (suggested merge_duplicate => reviewer must merge)
        is_fail_status = st in fail_statuses or (st == "duplicate" and action != "merged")
        if (args.mode == "submission" and sev in fail_sevs and is_fail_status
                and _is_confirmed_claim(r.get("finding_id"))):
            blocking.append({"finding_id": r.get("finding_id"), "severity": r.get("severity"),
                             "status": st, "action": action, "blockers": r.get("blockers"),
                             "warnings": r.get("warnings")})
        elif st in WARN_STATUSES or action in ("downgrade", "needs_runtime_poc", "merge_duplicate", "needs_manual_review"):
            warning.append({"finding_id": r.get("finding_id"), "severity": r.get("severity"),
                            "status": st, "action": action})

    override = os.environ.get("AUDITWATCH_CONFIRM_OVERRIDE") == "1"
    # eval mode NEVER blocks the candidate set; submission mode blocks unless overridden
    blocked = (args.mode == "submission" and bool(blocking) and not override)
    ts = datetime.now(timezone.utc).isoformat()
    out = {"generated_at": ts, "mode": args.mode, "strict": args.strict,
           "total": len(results), "blocking": blocking, "warnings": warning,
           "blocked": blocked, "override": override}
    (audit_path("output") / "confirm" / "confirm_gate.json").write_text(json.dumps(out, indent=2))

    if not args.quiet:
        verdict = "BLOCK" if blocked else "PASS"
        print(f"Confirm gate ({args.mode}{'/strict' if args.strict else ''}): {verdict}")
        print(f"  candidates {len(results)} · blocking {len(blocking)} · warnings {len(warning)}")
        for b in blocking[:10]:
            print(f"  BLOCK {b['finding_id']} [{b['severity']}] {b['status']} → {b['action']}")
        if args.mode == "eval":
            print("  (eval mode: advisory only — does not block the eval candidate set)")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
