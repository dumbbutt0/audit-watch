#!/usr/bin/env python3
"""
pre_poc_readiness.py — readiness gate before PoC work.

Intended trigger: PreToolUse on a Bash command running
`generate_poc_plan.py` / `generate_poc_test.py` / `run_poc_tests.py`.

Prevents wasted PoC effort on findings that haven't reached the human review pause or aren't
eligible. Severity is calibrated to cost:
    • FORK / expensive PoC (the plan requests an RPC fork)  → HARD-BLOCK on a readiness failure.
    • minimal local PoC (no fork)                            → WARN only (let it proceed).

Readiness checks (deterministic, cheap):
    1. output/review_gate.md exists — the pipeline reached the human selection pause.
    2. the target finding is eligible — present in data/triage/{poc_required,submit}.jsonl.

Fork detection: data/poc_queue/<id>_plan.json contains a truthy fork/rpc indicator
(needs_fork / fork / fork_url / rpc_url / fork_block_number) or the literal substring "fork".
If no plan exists yet (e.g. generate_poc_plan.py is being run for the first time), the PoC is
treated as not-yet-fork (warn) — the plan step itself is cheap.

Contract: exit 2 = block (reason on stderr), 0 = allow. AUDITWATCH_HOOK_OVERRIDE=1 bypasses.
Writes audits/<id>/data/gates/pre_poc/<finding-id>.json.

Run manually:  python scripts/hooks/pre_poc_readiness.py --finding-id ID [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _hooklib as h

_FORK_KEYS = ("needs_fork", "fork", "fork_url", "rpc_url", "fork_block_number", "fork_block")


def _is_fork_poc(finding_id: str | None) -> bool:
    if not finding_id:
        return False
    plan = h.audit_file("data/poc_queue", f"{finding_id}_plan.json")
    if plan is None or not plan.exists():
        return False
    try:
        data = json.loads(plan.read_text())
    except (json.JSONDecodeError, OSError):
        return False
    for k in _FORK_KEYS:
        v = data.get(k)
        if isinstance(v, bool) and v:
            return True
        if isinstance(v, (str, int)) and str(v).strip() and str(v).strip().lower() not in {"0", "false", "none"}:
            return True
    # Fallback: a fork is often described free-form in the plan text.
    return "fork" in json.dumps(data).lower()


def evaluate(finding_id: str | None) -> dict:
    reasons: list[str] = []

    review_gate = h.audit_file("output", "review_gate.md")
    if review_gate is None or not review_gate.exists():
        reasons.append("output/review_gate.md absent — pipeline has not reached the human review pause")

    eligible = h.ids_in_jsonl(h.audit_file("data/triage", "poc_required.jsonl")) \
        | h.ids_in_jsonl(h.audit_file("data/triage", "submit.jsonl"))
    if finding_id and finding_id not in eligible:
        reasons.append(f"{finding_id} not in poc_required/submit triage buckets (not human-selected)")
    elif finding_id is None:
        reasons.append("no finding id resolved — cannot confirm eligibility")

    return {
        "generated_at": h.now(),
        "finding_id": finding_id,
        "is_fork_poc": _is_fork_poc(finding_id),
        "passed": not reasons,
        "issues": reasons,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="PoC readiness gate (block forks, warn local)")
    ap.add_argument("--finding-id", default=None)
    ap.add_argument("--dry-run", action="store_true", help="Evaluate + print; never block, never write")
    args = ap.parse_args()

    payload = h.read_hook_input()
    finding_id = h.finding_id_from(payload, args.finding_id)

    result = evaluate(finding_id)
    slug = (finding_id or "unknown").replace("/", "_")
    h.write_gate_artifact(["pre_poc", f"{slug}.json"], result, dry_run=args.dry_run)

    if result["passed"]:
        print(f"[audit-watch hook] pre-poc OK — {finding_id or '(scope all)'} "
              f"(fork={result['is_fork_poc']})", file=sys.stderr)
        return h.ALLOW

    detail = "; ".join(result["issues"])
    if args.dry_run:
        print(f"[audit-watch hook] DRY-RUN: not ready ({'fork' if result['is_fork_poc'] else 'local'}) "
              f"— {detail}", file=sys.stderr)
        return h.ALLOW
    if h.override_active():
        return h.emit_warn(f"pre-poc readiness OVERRIDDEN: {detail}")
    if result["is_fork_poc"]:
        return h.emit_block(f"fork/expensive PoC not ready — {detail}")
    # minimal local PoC: warn, but allow.
    return h.emit_warn(f"PoC may not be ready (local test, allowed) — {detail}")


if __name__ == "__main__":
    sys.exit(main())
