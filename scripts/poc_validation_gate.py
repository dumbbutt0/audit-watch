#!/usr/bin/env python3
"""
poc_validation_gate.py — Mode-aware PoC validation gate (deterministic, no LLM).

Consumes output/poc_validation/poc_validation_results.json and enforces proof-quality requirements by mode.
It NEVER blocks eval (recall) mode — eval recall is never gated by PoCs. Engagement and submission modes
block findings whose PoCs do not meet the bar, and submission additionally blocks severity overclaim.

Modes:
  eval        PoCs not required. Warn on invalid/overclaimed PoC claims. Always PASS.
  engagement  High/Critical require validation_status=proven (or a manual waiver). Medium require
              >= partially_proven (or waiver). Low pass with static proof if impact is source-obvious.
  submission  High/Critical require proven. Medium require proven, or partially_proven WITH limitations.
              invalid_poc / inconclusive / setup_only / failed block. Severity overclaim blocks.

Manual waivers: output/poc_validation/waivers.json  ->  {"waived": ["FID-1", ...], "reason": {...}}
Override (escape hatch, logged): AUDITWATCH_POCGATE_OVERRIDE=1

Writes: output/poc_validation/poc_validation_gate.json   Exit: 0 PASS / 1 BLOCK (eval always 0).

Usage:
    python scripts/poc_validation_gate.py --mode eval|engagement|submission [--quiet]
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

SEV_RANK = {"Informational": 0, "Info": 0, "Low": 1, "Medium": 2, "High": 3, "Critical": 4, "Unknown": 2}


def _load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def evaluate(result: dict, mode: str, waived: set[str]) -> tuple[bool, str]:
    """Return (blocks, reason). blocks=True means this finding fails the gate in this mode."""
    fid = result["finding_id"]
    sev = result.get("claimed_severity", "Unknown")
    rank = SEV_RANK.get(sev, 2)
    status = result.get("validation_status")
    overclaim = result.get("severity_overclaim")
    has_limits = result.get("limitations") not in (None, "")

    if fid in waived:
        return False, "manual_waiver"

    if mode == "eval":
        return False, "eval_never_blocks"

    if mode == "engagement":
        if rank >= 3:  # High/Critical
            if status != "proven":
                return True, f"High/Critical requires proven PoC (got {status})"
        elif rank == 2:  # Medium
            if status not in ("proven", "partially_proven"):
                return True, f"Medium requires >= partially_proven (got {status})"
        else:  # Low/Info
            if status in ("invalid_poc", "setup_only"):
                return True, f"Low PoC is {status}"
        if overclaim:
            return True, "severity_overclaim"
        return False, "ok"

    if mode == "submission":
        if overclaim:
            return True, "severity_overclaim"
        if status in ("invalid_poc", "inconclusive", "setup_only", "failed"):
            return True, f"submission blocks status={status}"
        if rank >= 3:
            if status != "proven":
                return True, f"High/Critical requires proven (got {status})"
        elif rank == 2:
            if status == "proven":
                pass
            elif status == "partially_proven" and has_limits:
                pass
            else:
                return True, f"Medium requires proven or partially_proven+limitations (got {status})"
        return False, "ok"

    return True, f"unknown_mode:{mode}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["eval", "engagement", "submission"], default="eval")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    override = os.environ.get("AUDITWATCH_POCGATE_OVERRIDE", "").strip() in ("1", "true", "yes", "on")
    out = audit_path("output", "poc_validation")
    out.mkdir(parents=True, exist_ok=True)
    vres = _load_json(out / "poc_validation_results.json", {"results": []}) or {"results": []}
    waivers = _load_json(out / "waivers.json", {}) or {}
    waived = set(waivers.get("waived", []))

    blocking, warnings, ok = [], [], []
    for r in vres.get("results", []):
        blocks, reason = evaluate(r, args.mode, waived)
        rowinfo = {"finding_id": r["finding_id"], "severity": r.get("claimed_severity"),
                   "status": r.get("validation_status"), "reason": reason}
        if blocks:
            blocking.append(rowinfo)
        elif reason not in ("ok", "eval_never_blocks", "manual_waiver"):
            warnings.append(rowinfo)
        else:
            ok.append(rowinfo)
        # eval mode: surface invalid/overclaim claims as warnings (never blocks)
        if args.mode == "eval" and (r.get("severity_overclaim") or r.get("validation_status") in ("invalid_poc", "setup_only")):
            warnings.append({**rowinfo, "reason": "eval_warn_" + (r.get("validation_status") or "overclaim")})

    passed = (len(blocking) == 0) or (args.mode == "eval") or override
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "passed": passed,
        "override_active": override,
        "reviewed": len(vres.get("results", [])),
        "blocking": blocking,
        "warnings": warnings,
        "ok_count": len(ok),
        "waived": sorted(waived),
    }
    (out / "poc_validation_gate.json").write_text(json.dumps(report, indent=2))

    if not args.quiet:
        verdict = "PASS" if passed else "BLOCK"
        print(f"PoC validation gate [{args.mode}]: {verdict}" + (" (OVERRIDE)" if override and blocking else ""))
        print(f"  reviewed {report['reviewed']} · blocking {len(blocking)} · warnings {len(warnings)} · ok {len(ok)}")
        for b in blocking:
            print(f"    BLOCK {b['finding_id']} ({b['severity']}): {b['reason']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
