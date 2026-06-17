#!/usr/bin/env python3
"""
human_review_classifier.py — Routes triage'd findings to AI-confirmable vs human review.

Implements the Jason Hadex 90/10 principle: AI handles systematic analysis (90%);
human auditors handle novel patterns, creative cross-system attacks, and findings
that AI cannot confirm consistently (10%).

Reads data/triage/submit.jsonl and data/triage/poc_required.jsonl, applies eight
classification criteria, and routes findings to one of two queues.

A finding is routed to human_review_queue.jsonl if 2+ criteria trigger.

Criteria:
  1. kb_similarity < threshold   (novel pattern — not in knowledge base)
  2. confirmation_score < threshold  (AI cannot agree with itself)
  3. trace_depth >= 3             (multi-hop cross-contract chain)
  4. no_compound_pattern_match    (compound claim but no COMP-* match)
  5. cross_chain_or_upgrade_category  (high-complexity categories)
  6. critical_without_level2_poc  (Critical claim with no proven PoC)
  7. bsa_finding                  (behavioral divergence — needs human intent judgment)
  8. multi_pass_human_flag        (already flagged by multi_pass_confirm.py)

Writes:
  data/triage/human_review_queue.jsonl   — needs human auditor review
  data/triage/ai_confirmed.jsonl         — AI can handle autonomously

Usage:
    python scripts/human_review_classifier.py
    python scripts/human_review_classifier.py --dry-run
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from audit_context import audit_path

HUMAN_REVIEW_CATEGORIES = {"cross_chain", "upgrade_storage"}


def load_config() -> dict:
    policy_path = REPO_ROOT / "config" / "agent_policy.json"
    if policy_path.exists():
        return json.loads(policy_path.read_text())
    return {}


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


def write_jsonl(path: Path, records: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")


def query_kb_similarity(title: str, description: str) -> float:
    query = f"{title} {description[:200]}"
    try:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "retriever.py"), "other", query],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if data and isinstance(data, list) and len(data) > 0:
                # retriever returns findings with a similarity score field
                top = data[0]
                score = top.get("similarity", top.get("score", 0.0))
                return float(score)
    except Exception:
        pass
    # If retriever unavailable or errors, treat as novel (similarity 0)
    return 0.0


def load_confirmation_scores() -> dict[str, dict]:
    confirmed_path = audit_path("output") / "findings_confirmed.json"
    if not confirmed_path.exists():
        return {}
    try:
        data = json.loads(confirmed_path.read_text())
        return {
            f["id"]: {
                "confirmation_score": f.get("confirmation_score"),
                "human_review_required": f.get("human_review_required", False),
            }
            for f in data.get("findings", [])
        }
    except Exception:
        return {}


def load_poc_levels() -> dict[str, int]:
    poc_path = audit_path("data/runtime_poc") / "results.jsonl"
    levels = {}
    for rec in load_jsonl(poc_path):
        fid = rec.get("finding_id")
        if fid:
            levels[fid] = rec.get("runtime_level", 0)
    return levels


def load_compound_finding_ids() -> set[str]:
    compound_path = audit_path("output") / "findings_compound_synthesis.json"
    if not compound_path.exists():
        return set()
    try:
        data = json.loads(compound_path.read_text())
        ids = set()
        for f in data.get("findings", []):
            for component in f.get("compound_components", []):
                ids.add(component)
        return ids
    except Exception:
        return set()


def load_original_finding(finding_id: str) -> dict:
    output_dir = audit_path("output")
    for findings_file in output_dir.glob("findings_*.json"):
        if "confirmed" in findings_file.name:
            continue
        try:
            data = json.loads(findings_file.read_text())
            for f in data.get("findings", []):
                if f.get("id") == finding_id:
                    return f
        except Exception:
            pass
    return {}


def classify_finding(
    triage_rec: dict,
    cfg: dict,
    confirmation_scores: dict,
    poc_levels: dict,
    compound_ids: set,
    kb_threshold: float,
    conf_threshold: float,
    min_criteria: int,
) -> tuple[list[str], int]:
    finding_id = triage_rec.get("finding_id", triage_rec.get("id", ""))
    original = load_original_finding(finding_id)

    triggered = []

    # Criterion 1: KB similarity below threshold
    title = triage_rec.get("title", original.get("title", ""))
    description = original.get("description", "")
    kb_sim = query_kb_similarity(title, description)
    if kb_sim < kb_threshold:
        triggered.append(f"kb_similarity={kb_sim:.2f} < {kb_threshold:.2f}")

    # Criterion 2: Confirmation score below threshold
    conf_data = confirmation_scores.get(finding_id, {})
    conf_score = conf_data.get("confirmation_score")
    if conf_score is not None and conf_score < conf_threshold:
        triggered.append(f"confirmation_score={conf_score:.2f} < {conf_threshold:.2f}")

    # Criterion 3: Trace depth >= 3
    trace_depth = original.get("trace_depth", 0)
    if trace_depth >= 3:
        triggered.append(f"trace_depth={trace_depth}")

    # Criterion 4: Compound claim but no COMP-* match
    # Triggered if this finding is NOT in the compound synthesis components
    # but claims a compound-style finding (has multiple vuln types or cross-system description)
    vuln_type = original.get("vuln_type", "")
    is_compound_claim = "compound" in (triage_rec.get("title", "") + description).lower()
    if is_compound_claim and finding_id not in compound_ids:
        triggered.append("no_compound_pattern_match")

    # Criterion 5: Cross-chain or upgrade_storage category
    agent = original.get("agent", triage_rec.get("agent", ""))
    if agent in HUMAN_REVIEW_CATEGORIES or finding_id[:2] in ("CC", "US"):
        triggered.append(f"high_complexity_category ({agent})")

    # Criterion 6: Critical claim without Level 2+ PoC
    severity = triage_rec.get("recommended_severity", original.get("severity", ""))
    poc_level = poc_levels.get(finding_id, 0)
    if severity and severity.lower() == "critical" and poc_level < 2:
        triggered.append(f"critical_without_level2_poc (poc_level={poc_level})")

    # Criterion 7: BSA finding (behavioral divergence)
    if original.get("bsa_metadata"):
        triggered.append("bsa_finding")

    # Criterion 8: Already flagged by multi_pass_confirm
    if conf_data.get("human_review_required", False):
        triggered.append("multi_pass_human_flag")

    return triggered, len(triggered)


def compute_review_priority(
    finding: dict,
    triage_rec: dict,
    warn_count: int,
) -> float:
    """
    expected_value = P(valid) × expected_payout × novelty ÷ validation_cost

    Routes the highest-value findings to the top of the human review queue.
    """
    # P(valid): lower probability with more gate warnings
    p_valid = max(0.1, 1.0 - (warn_count * 0.15))

    # Expected payout: severity proxy
    sev_map = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.1}
    sev = triage_rec.get("recommended_severity", finding.get("severity", "low")).lower()
    payout = sev_map.get(sev, 0.1)

    # Novelty: low KB similarity = more novel = higher value
    # Inferred from human_review_reasons if available
    reasons = triage_rec.get("human_review_reasons", [])
    kb_sim_reason = next((r for r in reasons if r.startswith("kb_similarity=")), None)
    if kb_sim_reason:
        try:
            kb_sim = float(kb_sim_reason.split("=")[1].split(" ")[0])
        except (IndexError, ValueError):
            kb_sim = 0.5
    else:
        kb_sim = 0.5
    novelty = 1.0 - min(kb_sim, 1.0)

    # Validation cost: assumption count (more assumptions = harder to verify)
    assumption_count = finding.get("assumption_count", 3)
    cost = max(0.5, min(assumption_count / 5.0, 1.0))

    return round((p_valid * payout * novelty) / cost, 3)


def main():
    parser = argparse.ArgumentParser(description="Route findings to AI-confirmable vs human review")
    parser.add_argument("--dry-run", action="store_true", help="Print decisions without writing files")
    args = parser.parse_args()

    cfg = load_config()
    hr_cfg = cfg.get("human_review", {})
    kb_threshold = hr_cfg.get("kb_similarity_threshold", 0.4)
    conf_threshold_cfg = cfg.get("multi_pass", {}).get("confirmation_threshold", 0.6)
    min_criteria = hr_cfg.get("min_criteria_for_human_queue", 2)

    triage_dir = audit_path("data/triage")
    submit = load_jsonl(triage_dir / "submit.jsonl")
    poc_req = load_jsonl(triage_dir / "poc_required.jsonl")
    all_findings = submit + poc_req

    if not all_findings:
        print("No triage'd findings found. Run triage_findings.py first.")
        return

    confirmation_scores = load_confirmation_scores()
    poc_levels = load_poc_levels()
    compound_ids = load_compound_finding_ids()

    human_queue = []
    ai_confirmed_list = []
    timestamp = datetime.now(timezone.utc).isoformat()

    print(f"\nHuman review classification — {len(all_findings)} finding(s)\n")
    print(f"  KB similarity threshold: {kb_threshold}")
    print(f"  Confirmation threshold:  {conf_threshold_cfg}")
    print(f"  Min criteria for human: {min_criteria}\n")
    print(f"{'ID':<12} {'Severity':<10} {'Score':<8} {'Route':<16} {'Reasons'}")
    print("-" * 100)

    for rec in all_findings:
        finding_id = rec.get("finding_id", rec.get("id", "?"))
        severity = rec.get("recommended_severity", "?")

        triggered, score = classify_finding(
            rec, cfg, confirmation_scores, poc_levels, compound_ids,
            kb_threshold, conf_threshold_cfg, min_criteria,
        )

        needs_human = score >= min_criteria

        original = load_original_finding(finding_id)
        priority = compute_review_priority(original, rec, score) if needs_human else 0.0

        enriched = {
            **rec,
            "human_review_reasons": triggered,
            "human_review_score": score,
            "priority_score": priority,
            "classifier_timestamp": timestamp,
        }

        route = "⚠️  human review" if needs_human else "✅ AI confirmed"
        reasons_short = ", ".join(triggered[:2]) + ("..." if len(triggered) > 2 else "")
        print(f"{finding_id:<12} {severity:<10} {score:<8} {route:<16} {reasons_short}")

        if needs_human:
            human_queue.append(enriched)
        else:
            ai_confirmed_list.append(enriched)

    # Sort human queue by priority_score descending so highest-value findings surface first
    human_queue.sort(key=lambda x: x.get("priority_score", 0.0), reverse=True)

    print(f"\nSummary: {len(human_queue)} human review  |  {len(ai_confirmed_list)} AI confirmed")

    if args.dry_run:
        print("\n[dry-run] No files written.")
        return

    write_jsonl(triage_dir / "human_review_queue.jsonl", human_queue)
    write_jsonl(triage_dir / "ai_confirmed.jsonl", ai_confirmed_list)

    print(f"\n  Written: data/triage/human_review_queue.jsonl ({len(human_queue)} findings)")
    print(f"  Written: data/triage/ai_confirmed.jsonl ({len(ai_confirmed_list)} findings)")

    if human_queue:
        print("\n⚠️  Use /human-queue to review findings requiring expert validation.")


if __name__ == "__main__":
    main()
