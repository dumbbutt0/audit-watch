#!/usr/bin/env python3
"""
validate_triage_output.py — Post-triage schema validation.

Reads data/triage/submit.jsonl and poc_required.jsonl and checks that every
entry has the minimum fields required for a valid platform submission:
  - severity        (must not be unknown/empty)
  - triage_verdict  (must not be empty)
  - finding_id      (must not be empty)
  - title           (must not be empty)

47 findings with Unknown severity cannot be submitted to any platform.
This script is the catch before final_submission_pack.py runs.

Usage:
    python scripts/validate_triage_output.py
    python scripts/validate_triage_output.py --fix           # write corrected entries back
    python scripts/validate_triage_output.py --bucket poc    # check only poc_required.jsonl
    python scripts/validate_triage_output.py --strict        # exit 1 on any violation
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

TRIAGE_DIR = audit_path("data/triage")

SEVERITY_VALID = {"critical", "high", "medium", "low", "qa", "informational"}
VERDICT_VALID = {"submit", "poc_required", "downgrade", "merge", "reject"}

REQUIRED_FIELDS = {
    "finding_id": lambda v: bool(v and str(v).strip()),
    "title": lambda v: bool(v and str(v).strip()),
    "recommended_severity": lambda v: (v or "").strip().lower() in SEVERITY_VALID,
    "triage_status": lambda v: (v or "").strip().lower() in VERDICT_VALID,
}

FIELD_ALIASES = {
    "recommended_severity": ["severity", "final_severity"],
    "triage_status": ["triage_verdict", "decision", "verdict"],
}


def _resolve(record: dict, field: str) -> str:
    v = record.get(field, "")
    if not v:
        for alias in FIELD_ALIASES.get(field, []):
            v = record.get(alias, "")
            if v:
                break
    return v or ""


def validate_record(record: dict) -> list[str]:
    errors = []
    for field, check in REQUIRED_FIELDS.items():
        val = _resolve(record, field)
        if not check(val):
            errors.append(f"{field}={repr(val)}")
    return errors


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    results = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return results


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def fix_record(record: dict) -> tuple[dict, list[str]]:
    """Apply safe default repairs to a record. Returns (fixed_record, repairs_applied)."""
    repairs: list[str] = []
    r = dict(record)

    # Severity: try aliases, then default medium
    sev = _resolve(r, "recommended_severity").lower()
    if sev not in SEVERITY_VALID:
        for alias in FIELD_ALIASES["recommended_severity"]:
            candidate = (r.get(alias) or "").lower()
            if candidate in SEVERITY_VALID:
                r["recommended_severity"] = candidate
                repairs.append(f"severity: '' → '{candidate}' (from alias '{alias}')")
                break
        else:
            r["recommended_severity"] = "medium"
            repairs.append("severity: '' → 'medium' (default)")

    # triage_status: try aliases
    status = _resolve(r, "triage_status").lower()
    if status not in VERDICT_VALID:
        for alias in FIELD_ALIASES["triage_status"]:
            candidate = (r.get(alias) or "").lower()
            if candidate in VERDICT_VALID:
                r["triage_status"] = candidate
                repairs.append(f"triage_status: '' → '{candidate}' (from alias '{alias}')")
                break

    return r, repairs


def main() -> int:
    parser = argparse.ArgumentParser(description="Post-triage schema validation")
    parser.add_argument("--bucket", choices=["submit", "poc", "all"], default="all",
                        help="Which triage bucket to validate (default: all)")
    parser.add_argument("--fix", action="store_true",
                        help="Write corrected records back to the JSONL files")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 on any violation even when --fix is used")
    args = parser.parse_args()

    buckets = {
        "submit": TRIAGE_DIR / "submit.jsonl",
        "poc": TRIAGE_DIR / "poc_required.jsonl",
    }
    if args.bucket != "all":
        buckets = {args.bucket: buckets[args.bucket]}

    total_violations = 0
    total_records = 0

    for name, path in buckets.items():
        records = load_jsonl(path)
        if not records:
            print(f"  {name}: (empty or missing)")
            continue

        violations = []
        fixed_records = []

        for rec in records:
            errors = validate_record(rec)
            if errors:
                fid = rec.get("finding_id", "?")
                violations.append((fid, errors))
                if args.fix:
                    fixed, repairs = fix_record(rec)
                    fixed_records.append(fixed)
                    print(f"  [fix] {fid}: {'; '.join(repairs)}")
                else:
                    fixed_records.append(rec)
            else:
                fixed_records.append(rec)

        total_records += len(records)
        total_violations += len(violations)

        if violations:
            print(f"\n  {name}.jsonl — {len(violations)} violation(s):")
            for fid, errors in violations:
                print(f"    {fid}: {', '.join(errors)}")
        else:
            print(f"  {name}.jsonl — {len(records)} records OK")

        if args.fix and violations:
            write_jsonl(path, fixed_records)
            print(f"  Written {len(fixed_records)} records back to {path.name}")

    print(f"\nTotal: {total_records} records, {total_violations} violation(s)")

    if total_violations and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
