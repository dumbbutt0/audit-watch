#!/usr/bin/env python3
"""
triage_prepare.py — Deterministic pre-processor for the skill-in-session /triage flow.

Builds one self-contained bundle per finding so the /triage skill can reason in-session
(no API key). Each bundle = the finding + a source slice around its location + any gate/dupe
verdicts already computed. Writes bundles to data/triage/_bundles/<finding_id>.json and an
index data/triage/_bundles/index.json.

Pairs with: /triage skill (reasons) → triage_write.py (validates + writes buckets).

Usage:
    python scripts/triage_prepare.py
    python scripts/triage_prepare.py --context-lines 40
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, get_audit_root, load_jsonl, get_primary_contract_dir

CONTEXT_LINES = 30


def _load_merged() -> list[dict]:
    p = audit_path("output", "merged_findings.json")
    if not p.exists():
        raise SystemExit("[error] output/merged_findings.json not found. Run report_generator first.")
    data = json.loads(p.read_text())
    return data.get("findings", data if isinstance(data, list) else [])


def _resolve_source(file_field: str) -> Path | None:
    """Resolve a finding's location.file against the primary contract dir or audit root."""
    if not file_field:
        return None
    cand = Path(file_field)
    if cand.exists():
        return cand
    primary = get_primary_contract_dir()
    if primary:
        # try by suffix match within the primary dir
        name = Path(file_field).name
        hits = list(primary.rglob(name))
        if hits:
            return hits[0]
    root = get_audit_root()
    hits = list(root.rglob(Path(file_field).name))
    return hits[0] if hits else None


def _source_slice(loc: dict, ctx: int) -> str:
    f = _resolve_source(loc.get("file", ""))
    if not f or not f.is_file():
        return loc.get("code_snippet", "") or "(source not resolvable; using finding snippet)"
    try:
        lines = f.read_text(errors="ignore").splitlines()
    except OSError:
        return loc.get("code_snippet", "")
    start = max(0, int(loc.get("line_start", 1)) - 1 - ctx)
    end = min(len(lines), int(loc.get("line_end", loc.get("line_start", 1))) + ctx)
    numbered = [f"{i+1}: {lines[i]}" for i in range(start, end)]
    return "\n".join(numbered)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build per-finding triage bundles (deterministic)")
    ap.add_argument("--context-lines", type=int, default=CONTEXT_LINES)
    args = ap.parse_args()

    findings = _load_merged()
    gates = {r.get("finding_id"): r for r in load_jsonl(audit_path("data/triage", "gate_results.jsonl"))}
    dupes = {r.get("finding_id"): r for r in load_jsonl(audit_path("data/triage", "dupe_screen_results.jsonl"))}

    bundle_dir = audit_path("data/triage", "_bundles")
    bundle_dir.mkdir(parents=True, exist_ok=True)
    index = []

    for f in findings:
        fid = f.get("id") or f.get("finding_id")
        if not fid:
            continue
        loc = f.get("location", {}) or {}
        bundle = {
            "finding_id": fid,
            "title": f.get("title", ""),
            "agent": f.get("agent", ""),
            "claimed_severity": f.get("severity", ""),
            "claimed_confidence": f.get("confidence", ""),
            "location": loc,
            "description": f.get("description", ""),
            "impact": f.get("impact", ""),
            "ite": f.get("ite", {}),
            "ice_chain": f.get("ice_chain", {}),
            "source_slice": _source_slice(loc, args.context_lines),
            "gate_verdict": gates.get(fid, {}),
            "dupe_verdict": dupes.get(fid, {}),
            "is_safety_net_code": _looks_safety_net(loc.get("file", ""), f),
        }
        (bundle_dir / f"{fid}.json").write_text(json.dumps(bundle, indent=2))
        index.append({"finding_id": fid, "title": bundle["title"],
                      "claimed_severity": bundle["claimed_severity"],
                      "safety_net": bundle["is_safety_net_code"]})

    (bundle_dir / "index.json").write_text(json.dumps(index, indent=2))
    print(f"[ok] Wrote {len(index)} triage bundles → {bundle_dir}")
    print("     Next: run the /triage skill, then python scripts/triage_write.py")
    return 0


SAFETY_NET_HINTS = ("invariable", "sort", "oracle", "evaluate", "price", "bridge",
                    "season", "sunrise", "reseed", "migrat", "init", "guard", "solvency")


def _looks_safety_net(file_field: str, finding: dict) -> bool:
    hay = (file_field + " " + finding.get("title", "") + " " +
           (finding.get("location", {}) or {}).get("function", "")).lower()
    return any(h in hay for h in SAFETY_NET_HINTS)


if __name__ == "__main__":
    sys.exit(main())
