#!/usr/bin/env python3
"""
record_fp_autopsy.py — Record a false-positive autopsy for a rejected finding.

Extracts the original hypothesis, documents what was missed, derives a
reusable rejection rule, and writes to both per-audit and project-level
rejection_rules.jsonl.

Usage:
    python scripts/record_fp_autopsy.py \
        --finding-id RE-001 \
        --judge-outcome rejected \
        --rejection-reason "nonReentrant applied via ReentrancyGuard inheritance, agent missed it" \
        [--contest k2-kinetic-2026-04]
"""

import argparse
import json
import os
import sys
import time
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

MODEL = "claude-sonnet-4-6"
OUTPUT_DIR  = audit_path("output")
TRIAGE_DIR  = audit_path("data/triage")
FP_DIR      = audit_path("data/fp_autopsies")
LEARNING_DIR = audit_path("data/learning")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECT_FP_DIR = PROJECT_ROOT / "data" / "fp_autopsies"

VALID_OUTCOMES = {"rejected", "invalid", "duplicate", "downgraded", "out_of_scope"}

VALID_PATTERN_TYPES = [
    "inherited_guard",
    "admin_attacker",
    "bounded_impact",
    "impossible_state",
    "no_profitability",
    "non_exploitable",
    "unrealistic_liquidity",
    "requires_compromised_key",
    "unverifiable_assumption",
    "duplicate_pattern",
    "out_of_scope",
]

TAG_MAP = {
    "inherited_guard":        "already_guarded",
    "admin_attacker":         "admin_only",
    "impossible_state":       "impossible_state",
    "no_profitability":       "no_profitability",
    "non_exploitable":        "non_exploitable",
    "unrealistic_liquidity":  "unrealistic_liquidity",
    "requires_compromised_key": "requires_compromised_key",
    "unverifiable_assumption": "unverifiable_assumption",
    "duplicate_pattern":      "duplicate_pattern",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hex_ts() -> str:
    return hex(int(time.time()))[2:]


def load_finding_context(finding_id: str) -> dict:
    """Load original finding data from multiple pipeline artifacts."""
    context: dict = {"finding_id": finding_id}

    # From merged findings
    merged_path = OUTPUT_DIR / "merged_findings.json"
    if merged_path.exists():
        try:
            merged = json.loads(merged_path.read_text())
            for f in merged.get("findings", []):
                if f.get("id") == finding_id:
                    context["original_finding"] = f
                    break
        except json.JSONDecodeError:
            pass

    # From triage JSONL files
    for triage_file in ["submit.jsonl", "poc_required.jsonl", "rejected.jsonl", "downgraded.jsonl"]:
        tpath = TRIAGE_DIR / triage_file
        if not tpath.exists():
            continue
        for line in tpath.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if rec.get("finding_id") == finding_id:
                    context["triage_record"] = rec
                    break
            except json.JSONDecodeError:
                continue
        if "triage_record" in context:
            break

    # From defense map
    defense_path = OUTPUT_DIR / "defense_map.json"
    if defense_path.exists():
        try:
            dmap = json.loads(defense_path.read_text())
            mapping = dmap.get("defense_mappings", {}).get(finding_id)
            if mapping:
                context["defense_mapping"] = mapping
        except json.JSONDecodeError:
            pass

    return context


def extract_rejection_rule(
    client: anthropic.Anthropic,
    context: dict,
    rejection_reason: str,
    judge_outcome: str,
) -> dict | None:
    finding = context.get("original_finding", {})
    triage = context.get("triage_record", {})

    system_prompt = (
        "You are a smart contract auditing expert. "
        "Given a rejected finding, extract a reusable false-positive rejection rule. "
        "Focus on the STRUCTURAL PATTERN — the general class of mistake, not the specific finding. "
        "Output valid JSON only. No commentary."
    )

    user_content = (
        f"Rejected finding:\n"
        f"  ID: {context['finding_id']}\n"
        f"  vuln_type: {finding.get('vuln_type', 'unknown')}\n"
        f"  title: {finding.get('title', '')}\n"
        f"  severity claimed: {finding.get('severity', 'unknown')}\n"
        f"  judge outcome: {judge_outcome}\n"
        f"  rejection reason: {rejection_reason}\n"
        f"  triage attacker_type: {triage.get('attacker_model', {}).get('attacker_type', 'unknown')}\n"
        f"  defense coverage: {context.get('defense_mapping', {}).get('coverage', 'unknown')}\n\n"
        f"Extract a JSON rule with these fields:\n"
        f"  pattern_type: one of {VALID_PATTERN_TYPES}\n"
        f"  trigger_conditions: array of short strings (each a testable condition that identifies this pattern)\n"
        f"  rejection_reason: 1–2 sentences explaining why this pattern is a false positive\n"
        f"  vuln_type: the vuln_type this rule applies to (or 'all')\n"
        f"  agent: the agent that produced this finding (or 'any')\n"
        f"  confidence_threshold: 0.7–0.95 (how confident must the match be before auto-rejecting)\n"
        f"\nReturn ONLY the JSON object."
    )

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        raw = response.content[0].text.strip()
        # Strip code fences
        if raw.startswith("```"):
            import re
            raw = re.sub(r'^```[a-z]*\n?', '', raw)
            raw = re.sub(r'\n?```$', '', raw)
            raw = raw.strip()
        parsed = json.loads(raw)
    except Exception as e:
        print(f"  [warn] Rule extraction API error: {e}")
        return None

    pattern_type = parsed.get("pattern_type", "unverifiable_assumption")
    if pattern_type not in VALID_PATTERN_TYPES:
        pattern_type = "unverifiable_assumption"

    rule = {
        "rule_id": f"FP-{_hex_ts()}",
        "pattern_type": pattern_type,
        "trigger_conditions": parsed.get("trigger_conditions", []),
        "rejection_reason": parsed.get("rejection_reason", rejection_reason),
        "vuln_type": parsed.get("vuln_type", finding.get("vuln_type", "other")),
        "agent": parsed.get("agent", finding.get("_source_agent", "any")),
        "invalidation_tag": TAG_MAP.get(pattern_type, "unverifiable_assumption"),
        "confidence_threshold": float(parsed.get("confidence_threshold", 0.8)),
        "trust_level": 5,
        "created_at": _now(),
        "source_finding": context["finding_id"],
        "judge_outcome": judge_outcome,
    }
    return rule


def write_autopsy(finding_id: str, context: dict, rejection_reason: str, rule: dict | None) -> None:
    FP_DIR.mkdir(parents=True, exist_ok=True)
    autopsy = {
        "finding_id": finding_id,
        "original_hypothesis": context.get("original_finding", {}).get("title", ""),
        "claimed_severity": context.get("original_finding", {}).get("severity", "unknown"),
        "vuln_type": context.get("original_finding", {}).get("vuln_type", "unknown"),
        "rejection_reason": rejection_reason,
        "defense_coverage": context.get("defense_mapping", {}).get("coverage", "unknown"),
        "triage_score": context.get("triage_record", {}).get("score", {}).get("total"),
        "extracted_rule": rule,
        "recorded_at": _now(),
    }
    out_path = FP_DIR / f"{finding_id}_autopsy.json"
    out_path.write_text(json.dumps(autopsy, indent=2))
    print(f"  Wrote {out_path}")


def append_rule_to_jsonl(rule: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(rule) + "\n")


def append_to_severity_history(context: dict, rejection_reason: str, judge_outcome: str) -> None:
    """Feed this FP into the existing severity calibration learning file."""
    LEARNING_DIR.mkdir(parents=True, exist_ok=True)
    path = LEARNING_DIR / "severity_history.jsonl"
    record = {
        "finding_id": context["finding_id"],
        "claimed_severity": context.get("original_finding", {}).get("severity", "unknown"),
        "judged_severity": "invalid",
        "outcome": "false_positive",
        "rejection_reason": rejection_reason,
        "judge_outcome": judge_outcome,
        "vuln_type": context.get("original_finding", {}).get("vuln_type", "unknown"),
        "recorded_at": _now(),
    }
    with path.open("a") as f:
        f.write(json.dumps(record) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Record FP autopsy and extract rejection rule")
    parser.add_argument("--finding-id", required=True, help="Finding ID to record autopsy for")
    parser.add_argument("--judge-outcome", required=True,
                        choices=list(VALID_OUTCOMES), help="How the finding was judged")
    parser.add_argument("--rejection-reason", required=True, help="Why this finding was invalid")
    parser.add_argument("--contest", help="Contest/audit identifier (optional)")
    args = parser.parse_args()

    print(f"FP Autopsy Recorder — {args.finding_id}\n")

    context = load_finding_context(args.finding_id)
    if not context.get("original_finding"):
        print(f"  [warn] No finding data found for {args.finding_id} — recording partial autopsy")

    # Extract rule via Claude API
    client = require_llm(skill="fp_autopsy")
    rule = extract_rejection_rule(client, context, args.rejection_reason, args.judge_outcome)
    if rule:
        print(f"  Extracted rule: type={rule['pattern_type']}, tag={rule['invalidation_tag']}, "
              f"confidence={rule['confidence_threshold']}")
    else:
        print("  Rule extraction failed — autopsy recorded without rule")

    # Write autopsy JSON
    write_autopsy(args.finding_id, context, args.rejection_reason, rule)

    if rule:
        # Append to per-audit rules
        per_audit_path = FP_DIR / "rejection_rules.jsonl"
        append_rule_to_jsonl(rule, per_audit_path)
        print(f"  Appended to {per_audit_path}")

        # Append to project-level rules (shared across audits)
        PROJECT_FP_DIR.mkdir(parents=True, exist_ok=True)
        project_path = PROJECT_FP_DIR / "rejection_rules.jsonl"
        append_rule_to_jsonl(rule, project_path)
        print(f"  Appended to {project_path}")

    # Feed into severity calibration history
    append_to_severity_history(context, args.rejection_reason, args.judge_outcome)
    print(f"  Updated data/learning/severity_history.jsonl")

    print(f"\nAutopsy complete for {args.finding_id}")


if __name__ == "__main__":
    main()
