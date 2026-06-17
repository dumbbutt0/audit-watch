#!/usr/bin/env python3
"""
check_dedup.py — Guardrail-4 regression check.

Runs report_generator.deduplicate() on dedup_distinct.json and asserts the two distinct
oracle findings (same function name + vuln_type, DIFFERENT files) survive as separate findings.
Exits 0 on PASS, 1 on FAIL. Must FAIL before the report_generator fix and PASS after.

    python documentation/refinement/fixtures/check_dedup.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "scripts"))

import report_generator as rg  # noqa: E402

fixture = json.loads((Path(__file__).parent / "dedup_distinct.json").read_text())
findings = fixture["findings"]

out = rg.deduplicate([dict(f) for f in findings])
ids = sorted(f.get("id") for f in out)

ok = len(out) == 2 and ids == ["OR-001", "OR-002"]
collapsed = [f for f in out if f.get("_also_found_by")] + \
            [f for f in findings if f.get("duplicate_of")]

if ok and not any(f.get("duplicate_of") for f in out):
    print(f"PASS — both distinct findings survived: {ids}")
    sys.exit(0)
else:
    print(f"FAIL — expected 2 separate findings [OR-001, OR-002], got {len(out)}: {ids}")
    sys.exit(1)
