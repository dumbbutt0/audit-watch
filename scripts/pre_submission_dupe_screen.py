#!/usr/bin/env python3
"""
pre_submission_dupe_screen.py — Pre-submission public-report duplicate screening.

Runs BEFORE final_submission_pack.py. For each finding in submit.jsonl, queries
the Solodit KB, Immunefi bug-bounty reports, and the project-level duplicate
registry for similarity to known public reports.

Catches external duplicates that Gate 8 misses (Gate 8 only checks internal
cross-audit submissions and FP pattern similarity).

Decision thresholds:
  similarity >= 0.85 (any source) → action: "human_review"
  similarity >= 0.75              → action: "warn"
  otherwise                       → action: "pass"

Writes:
  data/triage/dupe_screen_results.jsonl   — per-finding screen result
  data/triage/human_review_queue.jsonl    — appended for human_review findings

Usage:
    python scripts/pre_submission_dupe_screen.py --all
    python scripts/pre_submission_dupe_screen.py --finding-id CC-001
    python scripts/pre_submission_dupe_screen.py --all --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

TRIAGE_DIR = audit_path("data/triage")
OUTPUT_DIR = audit_path("output")

WARN_THRESHOLD = 0.75
REVIEW_THRESHOLD = 0.85


# ─────────────────────────────────────────────────────────────────────────────
# Loaders
# ─────────────────────────────────────────────────────────────────────────────

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


def load_submitted_findings(finding_id: str | None) -> list[dict]:
    findings = load_jsonl(TRIAGE_DIR / "submit.jsonl")
    if finding_id:
        findings = [f for f in findings if f.get("finding_id") == finding_id]
    return findings


def load_duplicate_registry() -> list[dict]:
    path = PROJECT_ROOT / "data" / "duplicate_registry.jsonl"
    auto = PROJECT_ROOT / "data" / "auto_promoted_duplicate_registry.jsonl"
    return load_jsonl(path) + (load_jsonl(auto) if auto.exists() else [])


def load_merged_findings() -> dict[str, dict]:
    merged_path = OUTPUT_DIR / "merged_findings.json"
    if not merged_path.exists():
        return {}
    try:
        data = json.loads(merged_path.read_text())
        return {f.get("id", ""): f for f in data.get("findings", [])}
    except Exception:
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# Similarity queries
# ─────────────────────────────────────────────────────────────────────────────

def query_kb(vuln_type: str, title: str, description: str) -> float:
    query = f"{title} {description[:200]}"
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "tools" / "retriever.py"), vuln_type, query],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if data and isinstance(data, list):
                top = data[0]
                return float(top.get("similarity", top.get("score", 0.0)))
    except Exception:
        pass
    return 0.0


def query_immunefi(vuln_type: str, title: str, description: str) -> float:
    query = f"{title} {description[:200]}"
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "tools" / "immunefi_retriever.py"),
             vuln_type, query],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if data and isinstance(data, list):
                top = data[0]
                return float(top.get("similarity", top.get("score", 0.0)))
    except Exception:
        pass
    return 0.0


def registry_overlap(finding_vuln: str, title: str, description: str,
                     registry: list[dict]) -> tuple[float, str | None]:
    text = (title + " " + description).lower()
    best_score, best_id = 0.0, None
    for entry in registry:
        score = 0.0
        if entry.get("vuln_type") == finding_vuln:
            score += 0.4
        sig_tokens = entry.get("root_cause_signature", "").lower().split()
        hits = sum(1 for t in sig_tokens if len(t) > 3 and t in text)
        score += min(0.5, hits * 0.1)
        if best_score < score:
            best_score, best_id = score, entry.get("registry_id")
    return best_score, best_id


# ─────────────────────────────────────────────────────────────────────────────
# Decision
# ─────────────────────────────────────────────────────────────────────────────

def screen_finding(finding: dict, merged: dict[str, dict],
                   registry: list[dict]) -> dict:
    fid = finding.get("finding_id", "")
    title = finding.get("title", "")
    vuln_type = finding.get("vuln_type", "") or finding.get("finding_id", "logic")[:2].lower()

    # Enrich from merged_findings if possible
    merged_f = merged.get(fid, {})
    description = merged_f.get("description", "") or finding.get("reason", "")
    if not vuln_type:
        vuln_type = merged_f.get("vuln_type", "other")

    kb_sim = query_kb(vuln_type, title, description)
    immunefi_sim = query_immunefi(vuln_type, title, description)
    reg_score, reg_id = registry_overlap(vuln_type, title, description, registry)

    max_sim = max(kb_sim, immunefi_sim, reg_score)

    if max_sim >= REVIEW_THRESHOLD:
        action = "human_review"
        reason = "potential_duplicate_of_public_report"
    elif max_sim >= WARN_THRESHOLD:
        action = "warn"
        reason = "similarity_above_warn_threshold"
    else:
        action = "pass"
        reason = ""

    return {
        "finding_id": fid,
        "title": title,
        "kb_similarity": kb_sim,
        "immunefi_similarity": immunefi_sim,
        "registry_match": reg_id,
        "registry_score": reg_score,
        "action": action,
        "reason": reason,
        "screened_at": datetime.now(timezone.utc).isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Output
# ─────────────────────────────────────────────────────────────────────────────

def write_results_atomic(results: list[dict]):
    out_path = TRIAGE_DIR / "dupe_screen_results.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(".jsonl.tmp")
    with open(tmp, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    tmp.rename(out_path)
    return out_path


def append_to_human_review_queue(results: list[dict]):
    queue_path = TRIAGE_DIR / "human_review_queue.jsonl"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    with open(queue_path, "a") as f:
        for r in results:
            if r.get("action") == "human_review":
                entry = {
                    "finding_id": r["finding_id"],
                    "title": r.get("title", ""),
                    "human_review_reason": "dupe_screen_" + r.get("reason", ""),
                    "human_review_score": round(max(
                        r.get("kb_similarity", 0),
                        r.get("immunefi_similarity", 0),
                        r.get("registry_score", 0),
                    ), 3),
                    "classified_at": r.get("screened_at", ""),
                    "source": "pre_submission_dupe_screen",
                }
                if r.get("registry_match"):
                    entry["registry_match"] = r["registry_match"]
                f.write(json.dumps(entry) + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Pre-submission public-report duplicate screening"
    )
    parser.add_argument("--all", action="store_true", help="Screen all submitted findings")
    parser.add_argument("--finding-id", help="Screen a specific finding")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print results without writing files")
    args = parser.parse_args()

    if not args.all and not args.finding_id:
        parser.error("specify --all or --finding-id")

    print("Pre-Submission Duplicate Screen\n")

    findings = load_submitted_findings(args.finding_id)
    if not findings:
        print("  No submitted findings to screen.")
        return

    registry = load_duplicate_registry()
    merged = load_merged_findings()

    if registry:
        print(f"  Duplicate registry: {len(registry)} entries")
    print(f"  Screening {len(findings)} finding(s)...\n")

    results = []
    for finding in findings:
        fid = finding.get("finding_id", "?")
        print(f"  [{fid}] querying KB + Immunefi + registry...")
        result = screen_finding(finding, merged, registry)
        results.append(result)

        kb = result["kb_similarity"]
        imf = result["immunefi_similarity"]
        reg = result["registry_score"]
        action = result["action"]
        reg_match = f" (registry: {result['registry_match']})" if result.get("registry_match") else ""
        print(f"         kb={kb:.2f}  immunefi={imf:.2f}  registry={reg:.2f}{reg_match}  → {action}")

    if args.dry_run:
        print("\n[dry-run] Would write:")
        for r in results:
            print(f"  {r['finding_id']}: action={r['action']}, reason={r['reason']}")
        return

    out_path = write_results_atomic(results)
    print(f"\n  Written {len(results)} result(s) → {out_path.name}")

    human_review = [r for r in results if r["action"] == "human_review"]
    warns = [r for r in results if r["action"] == "warn"]
    passed = [r for r in results if r["action"] == "pass"]

    if human_review:
        append_to_human_review_queue(results)
        print(f"  Routed {len(human_review)} finding(s) to human_review_queue.jsonl")

    print(f"\nSummary: {len(passed)} pass | {len(warns)} warn | {len(human_review)} human_review")

    if human_review:
        print("\n⚠️  These findings need manual duplicate check before submitting:")
        for r in human_review:
            match_note = f" (matches registry {r['registry_match']})" if r.get("registry_match") else ""
            print(f"   {r['finding_id']}{match_note}")

    try:
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "generate_status.py")],
                       capture_output=True, timeout=30)
    except Exception:
        pass


if __name__ == "__main__":
    main()
