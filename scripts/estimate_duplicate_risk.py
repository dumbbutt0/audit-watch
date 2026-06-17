#!/usr/bin/env python3
"""
estimate_duplicate_risk.py — Duplicate Risk Estimation Agent.

Compares each finding against all others in the batch to identify shared
root causes and fixes. Writes per-finding risk scores and root cause clusters.

Usage:
    python scripts/estimate_duplicate_risk.py --all
    python scripts/estimate_duplicate_risk.py --finding-id LG-005
    python scripts/estimate_duplicate_risk.py --all --force
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

if Path(".env").exists():
    for _line in Path(".env").read_text().splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip("\"'"))

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path
from llm_runtime import require_llm  # no-silent-fail: actionable message instead of credit spend/crash

MODEL       = "claude-sonnet-4-6"
TRIAGE_DIR  = audit_path("data/triage")
DUP_DIR     = audit_path("data/duplicates")
EXPLOIT_DIR = audit_path("data/exploitability")
PROMPTS     = Path(__file__).resolve().parent.parent / "prompts"
OUTPUT_DIR  = audit_path("output")


# ─────────────────────────────────────────────────────────────────────────────
# Loaders
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


def load_existing(output_path: Path) -> dict[str, dict]:
    return {r["finding_id"]: r for r in load_jsonl(output_path) if "finding_id" in r}


def write_jsonl(records: dict[str, dict], path: Path) -> None:
    with path.open("w") as fh:
        for r in records.values():
            fh.write(json.dumps(r) + "\n")


def strip_fences(raw: str) -> str:
    if raw.startswith("```"):
        raw = re.sub(r'^```[a-z]*\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw)
    return raw.strip()


def load_merged_findings() -> dict[str, dict]:
    path = OUTPUT_DIR / "merged_findings.json"
    if not path.exists():
        return {}
    return {f["id"]: f for f in json.loads(path.read_text()).get("findings", [])}


def load_all_triage_findings(finding_id: str | None = None) -> list[dict]:
    items = (
        load_jsonl(TRIAGE_DIR / "submit.jsonl") +
        load_jsonl(TRIAGE_DIR / "poc_required.jsonl")
    )
    if finding_id:
        items = [i for i in items if i.get("finding_id") == finding_id]
    return items


# ─────────────────────────────────────────────────────────────────────────────
# API call
# ─────────────────────────────────────────────────────────────────────────────

def call_dup_agent(triage: dict, original: dict,
                   exploit_model: dict,
                   all_findings_context: list[dict]) -> dict:
    system = (PROMPTS / "duplicate_risk.md").read_text()

    user = json.dumps({
        "target_finding": {
            "finding_id":  triage.get("finding_id", ""),
            "title":       triage.get("title") or original.get("title", ""),
            "triage":      triage,
            "original":    original,
            "exploitability_model": exploit_model,
        },
        "batch_findings": all_findings_context,
    }, indent=2)

    client = require_llm(skill="estimate_duplicate_risk")
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    raw = strip_fences(response.content[0].text)
    result = json.loads(raw)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Per-finding processor
# ─────────────────────────────────────────────────────────────────────────────

def process_finding(triage: dict, original: dict, exploit_model: dict,
                    all_findings_context: list[dict],
                    existing: dict[str, dict], force: bool) -> dict:
    fid = triage.get("finding_id", "")
    ts  = datetime.now(timezone.utc).isoformat()

    if fid in existing and not force:
        print(f"  {fid}: already processed — skip")
        return existing[fid]

    print(f"  {fid}: estimating duplicate risk...", end=" ", flush=True)
    try:
        result = call_dup_agent(triage, original, exploit_model, all_findings_context)
        result["finding_id"] = fid
        result["analyzed_at"] = ts
        risk = result.get("duplicate_risk", "?")
        action = result.get("recommended_action", "?")
        print(f"risk={risk}  action={action}")
        return result
    except Exception as exc:
        print(f"ERROR: {exc}")
        return {
            "finding_id":    fid,
            "status":        "error",
            "error":         str(exc),
            "duplicate_risk": "low",
            "analyzed_at":   ts,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Cluster builder
# ─────────────────────────────────────────────────────────────────────────────

def build_clusters(results: dict[str, dict]) -> list[dict]:
    """Group findings by high/medium shared root cause pairs."""
    clusters: dict[frozenset, list[str]] = defaultdict(list)

    for fid, r in results.items():
        if r.get("status") == "error":
            continue
        for dup in r.get("internal_duplicates", []):
            if dup.get("shared_root_cause"):
                pair = frozenset([fid, dup["finding_id"]])
                clusters[pair].append(fid)

    output = []
    seen: set[frozenset] = set()
    for pair in clusters:
        if pair in seen:
            continue
        seen.add(pair)
        ids = list(pair)
        output.append({
            "cluster_id":     f"CLUSTER-{len(output)+1:03}",
            "findings":       ids,
            "risk_level":     results.get(ids[0], {}).get("duplicate_risk", "?"),
            "overlap_reason": results.get(ids[0], {}).get("overlap_reason", ""),
        })

    # Also add standalone high-risk findings
    for fid, r in results.items():
        if r.get("duplicate_risk") == "high" and not any(fid in c["findings"] for c in output):
            output.append({
                "cluster_id": f"CLUSTER-{len(output)+1:03}",
                "findings":   [fid],
                "risk_level": "high",
                "overlap_reason": r.get("overlap_reason", ""),
            })

    return output


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Duplicate Risk Estimation Agent")
    parser.add_argument("--finding-id", default=None)
    parser.add_argument("--all",   action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not args.finding_id and not args.all:
        parser.print_help()
        return 1

    DUP_DIR.mkdir(parents=True, exist_ok=True)
    output_path   = DUP_DIR / "risk.jsonl"
    clusters_path = DUP_DIR / "clusters.jsonl"

    merged      = load_merged_findings()
    exploit_map = {r["finding_id"]: r
                   for r in load_jsonl(EXPLOIT_DIR / "models.jsonl") if "finding_id" in r}
    existing    = load_existing(output_path)
    findings    = load_all_triage_findings(args.finding_id)

    if not findings:
        print(f"[error] No findings found{f' for {args.finding_id}' if args.finding_id else ''}")
        return 1

    # Build context for pairwise comparison (always all findings)
    all_triage = load_all_triage_findings()
    all_findings_context = [
        {
            "finding_id":    t.get("finding_id", ""),
            "title":         t.get("title") or merged.get(t.get("finding_id", ""), {}).get("title", ""),
            "vuln_type":     merged.get(t.get("finding_id", ""), {}).get("vuln_type", ""),
            "location":      merged.get(t.get("finding_id", ""), {}).get("location", {}),
            "description":   (merged.get(t.get("finding_id", ""), {}).get("description", "") or "")[:400],
            "recommendation": (merged.get(t.get("finding_id", ""), {}).get("recommendation", "") or "")[:200],
            "exploitability": exploit_map.get(t.get("finding_id", ""), {}).get("execution_sequence", []),
        }
        for t in all_triage
    ]

    print(f"Duplicate Risk Estimation — {len(findings)} finding(s)\n")

    results: dict[str, dict] = {**existing}
    new_results = []

    for triage in findings:
        fid          = triage.get("finding_id", "")
        original     = merged.get(fid, {})
        exploit_model = exploit_map.get(fid, {})
        # Context excludes the target finding itself
        context = [f for f in all_findings_context if f["finding_id"] != fid]
        result = process_finding(triage, original, exploit_model,
                                 context, existing, args.force)
        results[fid] = result
        new_results.append(result)

    write_jsonl(results, output_path)

    # Write clusters
    clusters = build_clusters(results)
    with clusters_path.open("w") as fh:
        for c in clusters:
            fh.write(json.dumps(c) + "\n")

    # Summary
    dist: dict[str, int] = {}
    high_pairs = []
    for r in new_results:
        risk = r.get("duplicate_risk", "error")
        dist[risk] = dist.get(risk, 0) + 1
        if risk == "high":
            high_pairs.append(r.get("finding_id", "?"))

    print(f"\n{'='*55}")
    print(f"  Risk distribution: {dist}")
    if high_pairs:
        print(f"  HIGH duplicate risk: {high_pairs}")
    print(f"  Clusters written → {clusters_path}")
    print(f"  Written → {output_path}")

    import subprocess as _sp
    _sp.run([sys.executable, str(Path(__file__).resolve().parent / "generate_status.py")],
            check=False, capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
