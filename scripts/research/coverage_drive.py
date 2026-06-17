#!/usr/bin/env python3
"""
coverage_drive.py — RESEARCH-ONLY orchestration to DRIVE discovery to 100% coverage so no in-scope item is left
unexamined ("never miss a bug because a file wasn't read").

Runs the EXISTING production coverage scripts (read-only invocation; never edits them) on the ACTIVE audit, in order:
  1. build_coverage_manifest    — refresh the denominator from SOURCE (every in-scope item; timeout-proof)
  2. init_coverage_dispositions — seed any new items as `unassigned` (idempotent; preserves existing)
  3. link_findings_to_manifest  — flip items that have findings to `finding`
  4. coverage_completeness_gate — report coverage% + the explicit unassigned/assigned (unexamined) gap list
  5. if unexamined > 0: coverage_sweep_prepare — stage per-file bundles, then print the next step:
        run the /coverage-sweep skill (examines each item) -> coverage_sweep_write -> re-run this driver.
Loops (resumable across runs) until `unassigned + assigned == 0` (the LLM examination is the /coverage-sweep skill).
This wrapper is the resumable harness around it; it sets NO disposition/severity and mints NO finding itself.

Report-partial mode: always exits 0 and prints the remaining gap; the production coverage_completeness_gate (called
here for its report) is the hard fail-closed block used at the review gate.

Usage: python scripts/research/coverage_drive.py [--no-rebuild]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_context import audit_path, get_active_audit  # noqa: E402

PY = sys.executable


def _run(args, **kw):
    return subprocess.run([PY] + args, cwd=str(ROOT), capture_output=True, text=True, **kw)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-rebuild", action="store_true", help="skip build_coverage_manifest (use existing)")
    a = ap.parse_args()
    try:
        active = get_active_audit().get("audit_id", "?")
    except Exception:
        active = "?"
    print(f"[coverage_drive] active audit: {active}")

    out = audit_path("output")
    steps = []
    if not a.no_rebuild:
        steps.append(["scripts/build_coverage_manifest.py"])
    steps += [["scripts/init_coverage_dispositions.py"],
              ["scripts/link_findings_to_manifest.py"]]
    for s in steps:
        r = _run(s)
        tag = Path(s[0]).stem
        print(f"  → {tag}: exit {r.returncode}" + (f"  {r.stdout.strip().splitlines()[-1]}" if r.stdout.strip() else ""))

    # report (no override -> true counts); the gate exits nonzero when blocking, which is expected while incomplete
    g = _run(["scripts/coverage_completeness_gate.py", "--quiet"])
    gate_path = out / "coverage_gate.json"
    if not gate_path.exists():
        print("  ! coverage_gate.json not produced; cannot assess coverage"); return 0
    gate = json.loads(gate_path.read_text())
    s = gate.get("summary", {})
    unexamined = s.get("unassigned", 0) + s.get("assigned_only", 0) + s.get("examined", 0)
    print(f"[coverage_drive] coverage {s.get('coverage_percent', 0)}% · in-scope {s.get('in_scope_items')} · "
          f"finding {s.get('finding')} · cleared {s.get('cleared')} · UNEXAMINED {unexamined} "
          f"(unassigned {s.get('unassigned')} + assigned {s.get('assigned_only')} + examined {s.get('examined')})")

    if unexamined == 0:
        print("[coverage_drive] COMPLETE — every in-scope item examined/cleared/finding/deferred. No silent gaps.")
        return 0

    # stage the next sweep batch and tell the operator the resumable next step
    prep = _run(["scripts/coverage_sweep_prepare.py"])
    print(f"  → coverage_sweep_prepare: exit {prep.returncode}"
          + (f"  {prep.stdout.strip().splitlines()[-1]}" if prep.stdout.strip() else ""))
    print(f"[coverage_drive] {unexamined} in-scope items still UNEXAMINED — NOT done. Next (resumable):")
    print("    1. Run the /coverage-sweep skill (examines the staged bundles per item).")
    print("    2. python scripts/coverage_sweep_write.py")
    print("    3. Re-run: python scripts/research/coverage_drive.py --no-rebuild   (loops until UNEXAMINED == 0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
