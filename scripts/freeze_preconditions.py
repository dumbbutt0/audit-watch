#!/usr/bin/env python3
"""
freeze_preconditions.py — block an eval freeze when required work was silently skipped.

Freezing an eval (snapshotting pre-answer-key artifacts) should not be allowed if the run quietly skipped
work that materially affects recall. This consolidates the conversion-engine guards into one precondition
check run BEFORE the manual sha256 freeze:

  1. specialist_coverage_gate — every mandatory specialist for the target profile actually ran
     (or is waived in output/specialist_waiver.json).
  2. deep_pass_ledger — no high-priority (tier 1-2) deep pass was skipped
     (or is waived in output/deep_pass_waiver.json).

Strict full-audit → exit 1 if either is blocking. Advisory mode → warn, exit 0. This is the gate the
"freeze should fail/warn if required specialists or high-priority deep passes were skipped" requirement maps
onto, given that the freeze itself is a manual sha256 step.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def _run(script: str) -> int:
    return subprocess.run([PY, str(ROOT / "scripts" / script), "--quiet"]).returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    full_audit = os.environ.get("AUDITWATCH_FULL_AUDIT") == "1"

    # Refresh the queue/ledger so the ledger reflects the latest dispositions.
    subprocess.run([PY, str(ROOT / "scripts" / "deep_pass_queue.py")],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    rc_spec = _run("specialist_coverage_gate.py")
    rc_ledger = _run("deep_pass_ledger.py")
    blocked = (rc_spec != 0) or (rc_ledger != 0)

    if not args.quiet:
        print("=== Freeze preconditions ===")
        print(f"  specialist coverage : {'BLOCK' if rc_spec else 'ok'}")
        print(f"  deep-pass budget    : {'BLOCK' if rc_ledger else 'ok'}")
        if blocked:
            print("  → FREEZE BLOCKED. Run the missing specialists / tier-1-2 deep passes, or record waivers "
                  "(output/specialist_waiver.json, output/deep_pass_waiver.json). See output/specialist_coverage.json "
                  "and output/deep_pass_budget_summary.json.")
        elif not full_audit:
            print("  (advisory mode — not blocking)")
        else:
            print("  → freeze preconditions satisfied.")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
