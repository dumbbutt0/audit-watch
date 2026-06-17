#!/usr/bin/env python3
"""
build_poc_queue.py — Build a prioritised PoC work queue from triage results.

Reads data/triage/poc_required.jsonl and data/triage/submit.jsonl (needs_poc=true).
Writes per-priority JSONL files to data/poc_queue/ and optionally to a single --out file.

Usage:
    python scripts/build_poc_queue.py                              # default: read triage, write p0-p3.jsonl
    python scripts/build_poc_queue.py --triage data/triage/poc_required.jsonl --out data/poc_queue/p0.jsonl
    python scripts/build_poc_queue.py --finding-id AR-001          # single finding
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

TRIAGE_DIR = audit_path("data/triage")
POC_DIR    = audit_path("data/poc_queue")

PRIORITY_ORDER = ["P0", "P1", "P2", "P3"]

# Bug type inference from vuln_type + impact
BUG_TYPE_MAP = {
    "arithmetic":          "arithmetic_unit_mismatch",
    "access-control":      "access_control_missing_auth",
    "reentrancy":          "reentrancy_cross_function",
    "oracle-manipulation": "oracle_manipulation",
    "oracle_config":       "oracle_config_bug",
    "dos":                 "dos_unbounded_loop",
    "logic-error":         "logic_error",
    "flash-loan":          "accounting_toctou",
    "other":               "other",
}

LOSS_TYPE_POC_APPROACH = {
    "fund_loss":     "unit_integration",
    "insolvency":    "pure_arithmetic",
    "permanent_lock": "state_machine",
    "temporary_dos": "unit_integration",
    "griefing":      "unit_integration",
    "accounting_error": "pure_arithmetic",
    "none":          "pure_arithmetic",
}


# ─────────────────────────────────────────────────────────────────────────────
# Priority
# ─────────────────────────────────────────────────────────────────────────────

def assign_priority(triage: dict) -> str:
    sev  = triage.get("recommended_severity", "low").lower()
    loss = triage.get("impact", {}).get("loss_type", "none").lower()
    if sev in ("critical", "high") and loss in ("fund_loss", "insolvency"):
        return "P0"
    if sev == "high" or (sev == "medium" and loss == "fund_loss"):
        return "P1"
    if sev == "medium" and loss in ("temporary_dos", "griefing"):
        return "P2"
    return "P3"


def infer_bug_type(triage: dict, original: dict) -> str:
    vt = original.get("vuln_type", "other")
    return BUG_TYPE_MAP.get(vt, "other")


def infer_poc_approach(triage: dict, bug_type: str) -> str:
    loss = triage.get("impact", {}).get("loss_type", "none")
    if "arithmetic" in bug_type or "rounding" in bug_type or "overflow" in bug_type:
        return "pure_arithmetic"
    if "reentrancy" in bug_type:
        return "mock_contract"
    if "toctou" in bug_type or "accounting" in bug_type:
        return "state_machine"
    return LOSS_TYPE_POC_APPROACH.get(loss, "unit_integration")


def build_source_locations(original: dict) -> list[str]:
    loc = original.get("location", {})
    if not loc:
        return []
    if isinstance(loc, str):
        return [loc] if loc else []
    parts = [loc.get("file", "")]
    fn = loc.get("function", "")
    if fn:
        parts[0] += f"::{fn}"
    ls = loc.get("line_start")
    le = loc.get("line_end")
    if ls and le:
        parts[0] += f" L{ls}-{le}"
    elif ls:
        parts[0] += f" L{ls}"
    return [p for p in parts if p]


# ─────────────────────────────────────────────────────────────────────────────
# Queue entry builder
# ─────────────────────────────────────────────────────────────────────────────

def load_merged_findings() -> dict[str, dict]:
    path = audit_path("output") / "merged_findings.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    return {f["id"]: f for f in data.get("findings", [])}


def build_queue_entry(triage: dict, merged: dict[str, dict]) -> dict:
    fid      = triage.get("finding_id", "")
    original = merged.get(fid, {})
    priority = assign_priority(triage)
    bug_type = infer_bug_type(triage, original)
    approach = infer_poc_approach(triage, bug_type)
    loc_raw  = original.get("location", {})
    loc      = loc_raw if isinstance(loc_raw, dict) else {"file": str(loc_raw), "function": None}

    # Language / framework from repo profile if available
    profile_path = POC_DIR / "repo_profile.json"
    language  = "rust"
    framework = "soroban"
    if profile_path.exists():
        profile   = json.loads(profile_path.read_text())
        language  = profile.get("language", "rust")
        framework = profile.get("framework", "soroban")

    return {
        "finding_id":       fid,
        "priority":         priority,
        "title":            triage.get("title") or original.get("title", ""),
        "target_contract":  loc.get("file", "").split("/")[-2] if "/" in loc.get("file", "") else "",
        "target_function":  loc.get("function", ""),
        "language":         language,
        "framework":        framework,
        "bug_type":         bug_type,
        "poc_approach":     approach,
        "claim_to_prove":   triage.get("impact", {}).get("severity_reason", "")[:200],
        "expected_result":  triage.get("exploitability", {}).get("profit_or_damage", ""),
        "required_setup":   triage.get("attacker_model", {}).get("required_preconditions", []),
        "source_locations": build_source_locations(original),
        "confidence":       triage.get("confidence", 3),
        "notes":            triage.get("decision_reason", "")[:300],
    }


# ─────────────────────────────────────────────────────────────────────────────
# I/O helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    items = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return items


def write_jsonl(items: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        for item in items:
            fh.write(json.dumps(item) + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Build PoC work queue from triage results")
    parser.add_argument("--triage",     default=None, help="Single triage JSONL file to read")
    parser.add_argument("--out",        default=None, help="Single output JSONL file")
    parser.add_argument("--finding-id", default=None, help="Process only this finding ID")
    args = parser.parse_args()

    POC_DIR.mkdir(parents=True, exist_ok=True)
    merged = load_merged_findings()

    # Load triage data
    if args.triage:
        triage_items = load_jsonl(Path(args.triage))
    else:
        triage_items = (
            load_jsonl(TRIAGE_DIR / "poc_required.jsonl") +
            [t for t in load_jsonl(TRIAGE_DIR / "submit.jsonl")
             if t.get("exploitability", {}).get("needs_poc")]
        )

    if args.finding_id:
        triage_items = [t for t in triage_items if t.get("finding_id") == args.finding_id]
        if not triage_items:
            print(f"[error] Finding {args.finding_id} not found in triage data")
            return 1

    # Build queue entries
    queue: list[dict] = [build_queue_entry(t, merged) for t in triage_items]
    queue.sort(key=lambda x: PRIORITY_ORDER.index(x["priority"]))

    if args.out:
        # Single output file
        write_jsonl(queue, Path(args.out))
        print(f"Wrote {len(queue)} entries → {args.out}")
    else:
        # Split by priority
        by_priority: dict[str, list[dict]] = {p: [] for p in PRIORITY_ORDER}
        for entry in queue:
            by_priority[entry["priority"]].append(entry)

        total_hours = 0
        print("Smart Contract Auditor — PoC Queue\n")
        for p in PRIORITY_ORDER:
            items = by_priority[p]
            if items:
                out_path = POC_DIR / f"{p.lower()}.jsonl"
                write_jsonl(items, out_path)
                hours = sum({"P0": 6, "P1": 4, "P2": 3, "P3": 2}[p] for _ in items)
                total_hours += hours
                print(f"  {p}: {len(items):2} findings → {out_path}  (~{hours}h)")

        print(f"\n  Total: {len(queue)} PoC tasks — estimated {total_hours} hours")

        # Also write combined queue to legacy location for backwards compat
        legacy = Path("data/triage/poc_queue.jsonl")
        write_jsonl(queue, legacy)

        # Print table
        print(f"\n  {'Priority':<8} {'ID':<10} {'Approach':<20} {'Title'}")
        print("  " + "-" * 75)
        for entry in queue:
            print(f"  {entry['priority']:<8} {entry['finding_id']:<10} "
                  f"{entry.get('poc_approach','?'):<20} {entry['title'][:40]}")

    import subprocess as _sp
    _sp.run([sys.executable, str(Path(__file__).resolve().parent / "generate_status.py")],
            check=False, capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
