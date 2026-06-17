"""
One-time script: inject PC findings (protocol_context agent) into the triage pipeline.

PC findings exist in output/merged_findings.json but were never fed through
triage_findings.py, so specialist scripts can't find them.  This script writes
minimal triage entries to data/triage/poc_required.jsonl (or rejected.jsonl for
Low-severity PC findings) so the full specialist pipeline can process them.

Usage:
    python scripts/register_pc_findings.py              # dry run (prints what would change)
    python scripts/register_pc_findings.py --apply      # write entries
    python scripts/register_pc_findings.py --all        # include Low/Info in poc_required too
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MERGED_JSON   = ROOT / "output" / "merged_findings.json"
TRIAGE_POC    = ROOT / "data" / "triage" / "poc_required.jsonl"
TRIAGE_REJ    = ROOT / "data" / "triage" / "rejected.jsonl"
TRIAGE_SUBMIT = ROOT / "data" / "triage" / "submit.jsonl"

SEV_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1, "informational": 0, "info": 0}


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def append_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")


def build_triage_entry(f: dict, triage_status: str) -> dict:
    fid      = f.get("id") or f.get("finding_id")
    raw_sev  = (f.get("severity") or "medium").lower()
    sev_rank = SEV_RANK.get(raw_sev, 2)
    score_total = max(10, sev_rank * 5)
    return {
        "finding_id":           fid,
        "triage_status":        triage_status,
        "agent":                f.get("agent", "protocol_context"),
        "title":                f.get("title", fid),
        "recommended_severity": raw_sev,
        "impact":               f.get("description", "")[:400],
        "decision_reason":      "Manually registered from merged_findings.json (protocol_context agent output)",
        "score": {
            "total":           score_total,
            "attacker_control": sev_rank,
            "impact_severity":  sev_rank,
            "exploitability":   max(1, sev_rank - 1),
            "novelty":          2,
            "protocol_impact":  sev_rank,
            "code_quality":     2,
        },
        "exploitability": {
            "needs_poc": triage_status == "poc_required",
            "reasoning": "Protocol context finding registered for specialist review",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Register PC findings into the triage pipeline")
    ap.add_argument("--apply", action="store_true", help="Write entries (default: dry run)")
    ap.add_argument("--all",   action="store_true", help="Put all PC findings in poc_required (including Low/Info)")
    args = ap.parse_args()

    if not MERGED_JSON.exists():
        print(f"[error] {MERGED_JSON} not found")
        return 1

    merged = json.loads(MERGED_JSON.read_text())
    all_findings = merged.get("findings") if isinstance(merged, dict) else merged or []

    pc_findings = [
        f for f in all_findings
        if (f.get("id") or f.get("finding_id") or "").startswith("PC-")
    ]

    if not pc_findings:
        print("[error] No PC findings found in output/merged_findings.json")
        return 1

    print(f"Found {len(pc_findings)} PC finding(s) in merged_findings.json\n")

    # Build set of already-registered IDs across all triage buckets.
    registered: set[str] = set()
    for path in (TRIAGE_SUBMIT, TRIAGE_POC, TRIAGE_REJ):
        for row in load_jsonl(path):
            fid = row.get("finding_id")
            if fid:
                registered.add(fid)

    poc_entries: list[dict] = []
    rej_entries: list[dict] = []

    for f in pc_findings:
        fid = f.get("id") or f.get("finding_id")
        if fid in registered:
            print(f"  [skip] {fid} — already in triage pipeline")
            continue
        raw_sev = (f.get("severity") or "medium").lower()
        rank    = SEV_RANK.get(raw_sev, 2)
        if args.all or rank >= 2:
            poc_entries.append(build_triage_entry(f, "poc_required"))
            print(f"  [poc_required] {fid} ({raw_sev}) — {f.get('title', '')[:60]}")
        else:
            rej_entries.append(build_triage_entry(f, "rejected"))
            print(f"  [rejected]     {fid} ({raw_sev}) — {f.get('title', '')[:60]}")

    if not poc_entries and not rej_entries:
        print("\n[ok] Nothing to register — all PC findings already in pipeline.")
        return 0

    print(f"\n  poc_required: {len(poc_entries)}  rejected: {len(rej_entries)}")

    if not args.apply:
        print("\n  Dry run — pass --apply to write entries.")
        return 0

    if poc_entries:
        append_jsonl(TRIAGE_POC, poc_entries)
        print(f"  Written {len(poc_entries)} entries → {TRIAGE_POC}")
    if rej_entries:
        append_jsonl(TRIAGE_REJ, rej_entries)
        print(f"  Written {len(rej_entries)} entries → {TRIAGE_REJ}")

    print("\n[done] PC findings registered. Run specialist review with:")
    ids = [e["finding_id"] for e in poc_entries]
    for fid in ids:
        print(f"  python scripts/run_specialist_review.py --finding-id {fid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
