#!/usr/bin/env python3
"""
pre_report_validate.py — HARD-BLOCK hook: gate report/submission packaging.

Intended trigger: PreToolUse on a Bash command running `final_submission_pack.py`.
Stops unvalidated, hard-rejected, or unproven findings from being packaged for submission —
enforcing the existing non-negotiables on the tool layer, regardless of entry path.

It REUSES existing gate scripts (does not re-derive their logic):
    1. validate_agent_output.py output/ --strict   — schema + zero-trust output validation.
    2. pre_submission_gate results (data/triage/gate_results.jsonl) — no packaged finding may
       carry overall_verdict == REJECT. If the gate never ran (file missing) → block.
    3. CLAUDE.md non-negotiable: every High/Critical finding being packaged must have a PROVED
       PoC (data/runtime_poc/results.jsonl status == "proved").

"Packaged findings" = the union of data/triage/{submit,poc_required}.jsonl (what
final_submission_pack.py reads). A specific --finding-id narrows the scope.

Contract: exit 2 = block (reason on stderr), 0 = allow. AUDITWATCH_HOOK_OVERRIDE=1 bypasses.
Writes audits/<id>/data/gates/pre_report/<scope>.json.

Run manually:  python scripts/hooks/pre_report_validate.py [--finding-id ID] [--dry-run]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _hooklib as h

_PROJECT_ROOT = h._SCRIPTS_DIR.parent
_HIGH_CRIT = {"high", "critical"}


def _packaged_ids(scope_id: str | None) -> set[str]:
    submit = h.ids_in_jsonl(h.audit_file("data/triage", "submit.jsonl"))
    pocreq = h.ids_in_jsonl(h.audit_file("data/triage", "poc_required.jsonl"))
    ids = submit | pocreq
    if scope_id:
        ids = {i for i in ids if i == scope_id}
    return ids


def _run_validate_agent_output() -> tuple[bool, str]:
    """Return (passed, detail). Reuses validate_agent_output.py --strict on output/."""
    out = h.audit_file("output")
    if out is None or not out.exists():
        return False, "no output/ directory for the active audit"
    script = _PROJECT_ROOT / "scripts" / "validate_agent_output.py"
    try:
        proc = subprocess.run(
            [sys.executable, str(script), str(out), "--strict"],
            capture_output=True, text=True, timeout=120,
        )
    except Exception as e:
        return False, f"validate_agent_output.py could not run: {e}"
    if proc.returncode != 0:
        tail = (proc.stdout or proc.stderr or "").strip().splitlines()[-3:]
        return False, "validate_agent_output --strict failed: " + " | ".join(tail)
    return True, "validate_agent_output --strict clean"


def evaluate(scope_id: str | None) -> dict:
    reasons: list[str] = []
    ids = _packaged_ids(scope_id)
    merged = h.merged_findings_index()
    proved = {r.get("finding_id") for r in
              h.load_jsonl(h.audit_file("data/runtime_poc", "results.jsonl"))
              if r.get("status") == "proved"}

    # 1. schema/zero-trust validation
    v_ok, v_detail = _run_validate_agent_output()
    if not v_ok:
        reasons.append(v_detail)

    # 2. pre_submission_gate must have run and not REJECT any packaged finding
    gate_path = h.audit_file("data/triage", "gate_results.jsonl")
    gate_rows = h.load_jsonl(gate_path)
    if not gate_rows:
        reasons.append("pre_submission_gate has not run (data/triage/gate_results.jsonl missing/empty)")
    else:
        verdict_by_id = {r.get("finding_id"): r.get("overall_verdict") for r in gate_rows}
        rejected = [i for i in ids if verdict_by_id.get(i) == "REJECT"]
        if rejected:
            reasons.append(f"packaged finding(s) hard-rejected by gate: {', '.join(sorted(rejected))}")

    # 3. High/Critical must have a proved PoC
    missing_poc = []
    for i in sorted(ids):
        sev = (merged.get(i, {}).get("severity", "") or "").lower()
        if sev in _HIGH_CRIT and i not in proved:
            missing_poc.append(f"{i}({sev})")
    if missing_poc:
        reasons.append("High/Critical without proved PoC: " + ", ".join(missing_poc))

    return {
        "generated_at": h.now(),
        "scope": scope_id or "all-packaged",
        "packaged_ids": sorted(ids),
        "passed": not reasons,
        "block_reasons": reasons,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Pre-report/submission validation gate (hard-block)")
    ap.add_argument("--finding-id", default=None)
    ap.add_argument("--dry-run", action="store_true", help="Evaluate + print; never block, never write")
    args = ap.parse_args()

    payload = h.read_hook_input()
    scope_id = h.finding_id_from(payload, args.finding_id)

    result = evaluate(scope_id)
    scope_slug = (scope_id or "all").replace("/", "_")
    h.write_gate_artifact(["pre_report", f"{scope_slug}.json"], result, dry_run=args.dry_run)

    if result["passed"]:
        print(f"[audit-watch hook] pre-report OK — {result['scope']} "
              f"({len(result['packaged_ids'])} finding(s))", file=sys.stderr)
        return h.ALLOW

    detail = "; ".join(result["block_reasons"])
    if args.dry_run:
        print(f"[audit-watch hook] DRY-RUN would block: {detail}", file=sys.stderr)
        return h.ALLOW
    if h.override_active():
        return h.emit_warn(f"pre-report issues OVERRIDDEN: {detail}")
    return h.emit_block(f"report packaging not ready — {detail}")


if __name__ == "__main__":
    sys.exit(main())
