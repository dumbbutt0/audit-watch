#!/usr/bin/env python3
"""
fp_pattern_check.py — Pre-triage false-positive pattern scan.

Reads per-audit and project-level rejection_rules.jsonl, compares each
finding against known FP patterns, and writes pattern_check_results.jsonl.

Run as Step 3.6 — after multi_pass_confirm, before pre_submission_gate.

Usage:
    python scripts/fp_pattern_check.py [--all] [--finding-id <ID>]
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

OUTPUT_DIR = audit_path("output")
TRIAGE_DIR  = audit_path("data/triage")
FP_DIR      = audit_path("data/fp_autopsies")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECT_FP_DIR = PROJECT_ROOT / "data" / "fp_autopsies"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_rejection_rules() -> list[dict]:
    """Load rules from per-audit and project-level files; deduplicate by rule_id."""
    rules: dict[str, dict] = {}

    # Project-level (broader corpus, lower precedence for dedup). The curated baseline takes
    # precedence over auto-promoted rules (dedup-by-rule_id keeps the first occurrence).
    for rules_path in [
        PROJECT_FP_DIR / "rejection_rules.jsonl",
        PROJECT_FP_DIR / "auto_promoted_rules.jsonl",
        FP_DIR / "rejection_rules.jsonl",
    ]:
        if not rules_path.exists():
            continue
        for line in rules_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rule = json.loads(line)
                rule_id = rule.get("rule_id", "")
                if rule_id and rule_id not in rules:
                    rules[rule_id] = rule
            except json.JSONDecodeError:
                continue

    return list(rules.values())


def _keyword_overlap(text_a: str, text_b: str) -> float:
    """Return 0.0–0.5 based on word overlap between two strings."""
    def words(s: str) -> set[str]:
        return set(re.findall(r'\b[a-z]{4,}\b', s.lower()))

    a_words = words(text_a)
    b_words = words(text_b)
    if not a_words or not b_words:
        return 0.0
    intersection = a_words & b_words
    union = a_words | b_words
    jaccard = len(intersection) / len(union)
    return min(jaccard * 1.5, 0.5)  # scale to max 0.5


def compute_rule_similarity(finding: dict, rule: dict) -> float:
    """Return 0.0–1.0 similarity between a finding and an FP rejection rule."""
    score = 0.0

    # Same vuln_type → +0.3
    if finding.get("vuln_type") == rule.get("vuln_type"):
        score += 0.3

    # Same source agent → +0.2
    if finding.get("_source_agent") == rule.get("agent"):
        score += 0.2

    # Keyword overlap between description and rejection_reason → up to +0.5
    desc = finding.get("description", "") + " " + (finding.get("impact", "") or "")
    reason = rule.get("rejection_reason", "")
    score += _keyword_overlap(desc, reason)

    # Trigger condition match bonus
    trigger_conditions = rule.get("trigger_conditions", [])
    desc_lower = desc.lower()
    matching_conditions = sum(1 for cond in trigger_conditions if cond.lower() in desc_lower)
    if trigger_conditions:
        score += 0.1 * (matching_conditions / len(trigger_conditions))

    return min(score, 1.0)


def check_against_rules(
    finding: dict,
    rules: list[dict],
    threshold: float = 0.6,
) -> list[dict]:
    """Return rules above threshold, sorted by similarity descending."""
    matches = []
    for rule in rules:
        sim = compute_rule_similarity(finding, rule)
        if sim >= threshold:
            matches.append({
                "rule_id": rule.get("rule_id"),
                "similarity": round(sim, 3),
                "pattern_type": rule.get("pattern_type"),
                "rejection_reason": rule.get("rejection_reason", ""),
                "vuln_type": rule.get("vuln_type"),
                "invalidation_tag": rule.get("invalidation_tag"),
                "confidence_threshold": rule.get("confidence_threshold", 0.8),
                "trust_level": rule.get("trust_level", 5),
            })
    return sorted(matches, key=lambda x: x["similarity"], reverse=True)


def compute_recommended_action(matches: list[dict]) -> str:
    if not matches:
        return "proceed"
    top = matches[0]
    if top["similarity"] > 0.85 and top["confidence_threshold"] > 0.8:
        return "reject"
    if top["similarity"] > 0.6:
        return "review"
    return "proceed"


def load_all_findings() -> list[dict]:
    findings = []
    for path in sorted(OUTPUT_DIR.glob("findings_*.json")):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        agent = data.get("agent", "")
        if agent == "protocol_context":
            continue
        for f in data.get("findings", []):
            f["_source_agent"] = agent
            findings.append(f)
    return findings


def check_finding(finding: dict, rules: list[dict]) -> dict:
    fid = finding.get("id", "?")
    matches = check_against_rules(finding, rules)
    action = compute_recommended_action(matches)
    return {
        "finding_id": fid,
        "matching_rules": matches,
        "top_similarity": matches[0]["similarity"] if matches else 0.0,
        "recommended_action": action,
        "checked_at": _now(),
    }


def main():
    parser = argparse.ArgumentParser(description="Pre-triage FP pattern check")
    parser.add_argument("--all", action="store_true", help="Check all findings")
    parser.add_argument("--finding-id", help="Check a specific finding by ID")
    args = parser.parse_args()

    print("FP Pattern Check — Step 3.6\n")

    rules = load_rejection_rules()
    print(f"  Loaded {len(rules)} rejection rules")

    if not rules:
        print("  No rules found — all findings proceed (first run)")
        # Write empty results so downstream scripts don't crash
        FP_DIR.mkdir(parents=True, exist_ok=True)
        (FP_DIR / "pattern_check_results.jsonl").write_text("")
        return

    findings = load_all_findings()
    if args.finding_id:
        findings = [f for f in findings if f.get("id") == args.finding_id]

    print(f"  Checking {len(findings)} findings against {len(rules)} FP rules")

    results: list[dict] = []
    reject_count = 0
    review_count = 0

    for finding in findings:
        result = check_finding(finding, rules)
        results.append(result)

        action = result["recommended_action"]
        if action == "reject":
            reject_count += 1
            fid = result["finding_id"]
            top_reason = result["matching_rules"][0]["rejection_reason"][:70] if result["matching_rules"] else ""
            print(f"  [REJECT] {fid}: similarity={result['top_similarity']:.2f} — {top_reason}")
        elif action == "review":
            review_count += 1

    FP_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FP_DIR / "pattern_check_results.jsonl"
    out_path.write_text("\n".join(json.dumps(r) for r in results) + ("\n" if results else ""))

    print(f"\n  Results: {reject_count} reject, {review_count} review, "
          f"{len(findings) - reject_count - review_count} proceed")
    print(f"  Wrote {out_path}")


if __name__ == "__main__":
    main()
