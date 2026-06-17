#!/usr/bin/env python3
"""
bulk_fp_autopsy.py — Batch-process all rejected findings across audits into FP rules.

Walks every audit workspace, reads rejected.jsonl, extracts rejection reasons,
and calls record_fp_autopsy.py logic to build rejection rules for the
project-level rejection_rules.jsonl corpus.

This is the one-time catch-up command that turns 297 silent rejections into
297 learned FP rules. Run once, then record_fp_autopsy.py handles incremental updates.

Usage:
    python scripts/bulk_fp_autopsy.py [--dry-run] [--audit <audit_id>] [--limit N]
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
from audit_context import list_audits
from llm_runtime import require_llm  # no-silent-fail: actionable message instead of credit spend/crash

ROOT = Path(__file__).resolve().parent.parent
PROJECT_FP_DIR = ROOT / "data" / "fp_autopsies"
MODEL = "claude-sonnet-4-6"

VALID_PATTERN_TYPES = [
    "inherited_guard", "admin_attacker", "bounded_impact", "impossible_state",
    "no_profitability", "non_exploitable", "unrealistic_liquidity",
    "requires_compromised_key", "unverifiable_assumption", "duplicate_pattern",
    "out_of_scope",
]

TAG_MAP = {
    "inherited_guard":          "already_guarded",
    "admin_attacker":           "admin_only",
    "impossible_state":         "impossible_state",
    "no_profitability":         "no_profitability",
    "non_exploitable":          "non_exploitable",
    "unrealistic_liquidity":    "unrealistic_liquidity",
    "requires_compromised_key": "requires_compromised_key",
    "unverifiable_assumption":  "unverifiable_assumption",
    "duplicate_pattern":        "duplicate_pattern",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hex_ts() -> str:
    return hex(int(time.time() * 1000))[2:]


def load_existing_rules(path: Path) -> set[str]:
    """Return set of source_finding IDs already in rules file."""
    if not path.exists():
        return set()
    seen: set[str] = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            sf = rec.get("source_finding")
            if sf:
                seen.add(sf)
        except json.JSONDecodeError:
            continue
    return seen


def load_rejected_findings(audit_dir: Path) -> list[dict]:
    rej_path = audit_dir / "data" / "triage" / "rejected.jsonl"
    if not rej_path.exists():
        return []
    findings = []
    for line in rej_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            findings.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return findings


def load_merged_finding(audit_dir: Path, finding_id: str) -> dict:
    merged = audit_dir / "output" / "merged_findings.json"
    if not merged.exists():
        return {}
    try:
        data = json.loads(merged.read_text())
        for f in data.get("findings", []):
            if f.get("id") == finding_id:
                return f
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def extract_rejection_reason(triage_rec: dict) -> str:
    """Extract the best available rejection reason from a triage record."""
    candidates = [
        triage_rec.get("decision_reason", ""),
        triage_rec.get("rejection_reason", ""),
        triage_rec.get("invalidation_reason", ""),
    ]
    quality = triage_rec.get("quality_gate", {}) or {}
    if quality.get("speculative_language"):
        candidates.append(f"speculative language detected: {quality['speculative_language']}")

    invalidation_tags = triage_rec.get("invalidation_tags", []) or []
    if invalidation_tags:
        candidates.append(f"invalidation tags: {', '.join(invalidation_tags)}")

    score = triage_rec.get("score", {}) or {}
    total = score.get("total")
    if total is not None and total < 16:
        candidates.append(f"triage score too low ({total}/35)")

    for c in candidates:
        if c and c.strip():
            return c.strip()

    return "rejected during triage (reason not recorded)"


def call_claude_for_rule(
    client: anthropic.Anthropic,
    finding_id: str,
    vuln_type: str,
    title: str,
    severity: str,
    rejection_reason: str,
    attacker_type: str,
    defense_coverage: str,
) -> dict | None:
    system = (
        "You are a smart contract auditing expert. "
        "Given a rejected finding, extract a reusable false-positive rejection rule. "
        "Focus on the STRUCTURAL PATTERN — the general class of mistake, not the specific finding. "
        "Output valid JSON only. No commentary."
    )

    user = (
        f"Rejected finding:\n"
        f"  ID: {finding_id}\n"
        f"  vuln_type: {vuln_type}\n"
        f"  title: {title}\n"
        f"  claimed severity: {severity}\n"
        f"  rejection reason: {rejection_reason}\n"
        f"  attacker_type: {attacker_type}\n"
        f"  defense_coverage: {defense_coverage}\n\n"
        f"Extract a JSON rule with fields:\n"
        f"  pattern_type: one of {VALID_PATTERN_TYPES}\n"
        f"  trigger_conditions: array of short testable strings\n"
        f"  rejection_reason: 1-2 sentences (general pattern, not specific finding)\n"
        f"  vuln_type: applies to (or 'all')\n"
        f"  agent: producing agent (or 'any')\n"
        f"  confidence_threshold: 0.7-0.95\n"
        f"\nReturn ONLY the JSON object."
    )

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=512,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        raw = resp.content[0].text.strip()
        if raw.startswith("```"):
            import re
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw).strip()
        parsed = json.loads(raw)
    except Exception as e:
        print(f"    [warn] Claude API error: {e}")
        return None

    pattern_type = parsed.get("pattern_type", "unverifiable_assumption")
    if pattern_type not in VALID_PATTERN_TYPES:
        pattern_type = "unverifiable_assumption"

    return {
        "rule_id": f"FP-{_hex_ts()}",
        "pattern_type": pattern_type,
        "trigger_conditions": parsed.get("trigger_conditions", []),
        "rejection_reason": parsed.get("rejection_reason", rejection_reason),
        "vuln_type": parsed.get("vuln_type", vuln_type or "other"),
        "agent": parsed.get("agent", "any"),
        "invalidation_tag": TAG_MAP.get(pattern_type, "unverifiable_assumption"),
        "confidence_threshold": float(parsed.get("confidence_threshold", 0.8)),
        "trust_level": 5,
        "created_at": _now(),
        "source_finding": finding_id,
        "judge_outcome": "rejected",
        "_bulk_import": True,
    }


def _write_rule(rule: dict, project_fp_dir: Path, per_audit_fp_dir: Path | None,
                dry_run: bool) -> None:
    """Write rule to project-level and optionally per-audit fp_autopsies/rejection_rules.jsonl."""
    if dry_run:
        return
    project_fp_dir.mkdir(parents=True, exist_ok=True)
    with (project_fp_dir / "rejection_rules.jsonl").open("a") as f:
        f.write(json.dumps(rule) + "\n")
    if per_audit_fp_dir is not None:
        per_audit_fp_dir.mkdir(parents=True, exist_ok=True)
        with (per_audit_fp_dir / "rejection_rules.jsonl").open("a") as f:
            f.write(json.dumps(rule) + "\n")


def load_duplicate_registry() -> list[dict]:
    path = ROOT / "data" / "duplicate_registry.jsonl"
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


def make_duplicate_pattern_rule(fid: str, vuln_type: str, registry_entry: dict) -> dict:
    """Generate a hardcoded duplicate_pattern rule from a confirmed duplicate registry entry."""
    sig_tokens = registry_entry.get("root_cause_signature", "").split()
    return {
        "rule_id": f"FP-{_hex_ts()}-dup",
        "pattern_type": "duplicate_pattern",
        "trigger_conditions": sig_tokens[:8],
        "rejection_reason": (
            f"Confirmed duplicate of {registry_entry.get('platform', 'Immunefi')} report "
            f"{registry_entry.get('duplicate_of_report', '?')}. "
            f"Root cause: {registry_entry.get('title', '')}"
        ),
        "vuln_type": vuln_type or registry_entry.get("vuln_type", "other"),
        "agent": "any",
        "invalidation_tag": "duplicate_pattern",
        "confidence_threshold": 0.9,
        "trust_level": 5,
        "created_at": _now(),
        "source_finding": fid,
        "judge_outcome": "duplicate",
        "_bulk_import": True,
        "_duplicate_registry_id": registry_entry.get("registry_id", ""),
    }


def process_submitted_duplicates(
    audit_id: str,
    audit_dir: Path,
    dup_registry: list[dict],
    existing_rules: set[str],
    dry_run: bool,
) -> int:
    """Write duplicate_pattern rules for submitted findings that match the duplicate registry."""
    if not dup_registry:
        return 0

    submit_path = audit_dir / "data" / "triage" / "submit.jsonl"
    if not submit_path.exists():
        return 0

    submit_recs = []
    for line in submit_path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                submit_recs.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    registry_by_audit_fid = {
        (e.get("our_audit"), e.get("our_finding_id")): e
        for e in dup_registry
    }

    written = 0
    for rec in submit_recs:
        fid = rec.get("finding_id", "")
        if not fid or fid in existing_rules:
            continue
        key = (audit_id, fid)
        if key not in registry_by_audit_fid:
            continue

        entry = registry_by_audit_fid[key]
        original = load_merged_finding(audit_dir, fid)
        vuln_type = original.get("vuln_type") or rec.get("vuln_type", entry.get("vuln_type", ""))

        print(f"    {fid}: confirmed duplicate → {entry.get('duplicate_of_report')}")
        if dry_run:
            print(f"      [dry-run] would write duplicate_pattern rule")
            written += 1
            continue

        rule = make_duplicate_pattern_rule(fid, vuln_type, entry)
        per_audit_fp_dir = audit_dir / "data" / "fp_autopsies"
        _write_rule(rule, PROJECT_FP_DIR, per_audit_fp_dir, dry_run=False)
        existing_rules.add(fid)
        print(f"      → rule_id={rule['rule_id']} tag=duplicate_pattern")
        written += 1

    return written


_TAG_KEYWORDS: list[tuple[list[str], str]] = [
    (["inherited", "guard", "reentrancy", "nonreentrant", "modifier", "openzeppelin"], "inherited_guard"),
    (["admin", "owner", "privileged", "only_admin", "only_owner"], "admin_attacker"),
    (["impossible", "unreachable", "never", "cannot happen", "invariant"], "impossible_state"),
    (["no profit", "bounded", "cost exceeds", "unprofitable", "no damage"], "no_profitability"),
    (["out of scope", "layer2", "off-chain", "L2", "centralized"], "out_of_scope"),
    (["duplicate", "known issue", "previously reported", "same root"], "duplicate_pattern"),
    (["not exploitable", "cannot be triggered", "blocked", "protected"], "non_exploitable"),
    (["unrealistic", "liquidity", "market condition", "oracle assumption"], "unrealistic_liquidity"),
    (["compromised key", "private key", "trusted signer"], "requires_compromised_key"),
]


def _heuristic_pattern_type(rejection_reason: str, invalidation_tags: list[str]) -> str:
    """Guess pattern_type from rejection reason text without calling Claude."""
    text = rejection_reason.lower()
    for keywords, pattern in _TAG_KEYWORDS:
        if sum(1 for kw in keywords if kw in text) >= 2:
            return pattern
    if invalidation_tags:
        tag = invalidation_tags[0]
        reverse = {v: k for k, v in TAG_MAP.items()}
        return reverse.get(tag, "unverifiable_assumption")
    return "unverifiable_assumption"


def make_nollm_rule(fid: str, vuln_type: str, rejection_reason: str,
                    invalidation_tags: list[str]) -> dict:
    """Generate a rule from rejection_reason without calling Claude."""
    pattern_type = _heuristic_pattern_type(rejection_reason, invalidation_tags)
    trigger_words = [w for w in rejection_reason.lower().split() if len(w) > 4][:6]
    return {
        "rule_id": f"FP-{_hex_ts()}-nollm",
        "pattern_type": pattern_type,
        "trigger_conditions": trigger_words,
        "rejection_reason": rejection_reason[:300],
        "vuln_type": vuln_type or "other",
        "agent": "any",
        "invalidation_tag": TAG_MAP.get(pattern_type, "unverifiable_assumption"),
        "confidence_threshold": 0.75,
        "trust_level": 2,
        "created_at": _now(),
        "source_finding": fid,
        "judge_outcome": "rejected",
        "_bulk_import": True,
        "_no_llm": True,
    }


def process_audit(
    audit_id: str,
    audit_dir: Path,
    client: anthropic.Anthropic | None,
    existing_rules: set[str],
    dry_run: bool,
    limit: int | None,
    dup_registry: list[dict] | None = None,
    no_llm: bool = False,
) -> tuple[int, int]:
    """Returns (processed, skipped)."""
    rejected = load_rejected_findings(audit_dir)
    per_audit_fp_dir = audit_dir / "data" / "fp_autopsies"

    submitted_dup_count = 0
    if dup_registry:
        submitted_dup_count = process_submitted_duplicates(
            audit_id, audit_dir, dup_registry, existing_rules, dry_run
        )

    if not rejected:
        return submitted_dup_count, 0

    print(f"\n  [{audit_id}] {len(rejected)} rejected findings")
    processed = submitted_dup_count
    skipped = 0

    for rec in rejected:
        fid = rec.get("finding_id", "")
        if not fid:
            skipped += 1
            continue

        if fid in existing_rules:
            print(f"    {fid}: skip (rule exists)")
            skipped += 1
            continue

        if limit is not None and (processed - submitted_dup_count) >= limit:
            print(f"    ... limit reached ({limit})")
            break

        original = load_merged_finding(audit_dir, fid)
        rejection_reason = extract_rejection_reason(rec)
        vuln_type = original.get("vuln_type") or rec.get("vuln_type", "")
        title = original.get("title") or rec.get("title", fid)
        severity = original.get("severity") or rec.get("recommended_severity", "")
        attacker_type = (rec.get("attacker_model") or {}).get("attacker_type", "unknown")
        defense_coverage = (rec.get("defense_analysis") or {}).get("coverage", "unknown")
        invalidation_tags = rec.get("invalidation_tags", []) or []

        print(f"    {fid} ({vuln_type}): {rejection_reason[:60]}...")

        if dry_run:
            print(f"      [dry-run] would extract rule {'(no-llm)' if no_llm else '(claude)'}")
            processed += 1
            continue

        if no_llm:
            rule = make_nollm_rule(fid, vuln_type, rejection_reason, invalidation_tags)
            _write_rule(rule, PROJECT_FP_DIR, per_audit_fp_dir, dry_run=False)
            existing_rules.add(fid)
            print(f"      → rule_id={rule['rule_id']} pattern={rule['pattern_type']} trust=2 (no-llm)")
        else:
            rule = call_claude_for_rule(
                client, fid, vuln_type, title, severity,
                rejection_reason, attacker_type, defense_coverage,
            )
            if rule:
                _write_rule(rule, PROJECT_FP_DIR, per_audit_fp_dir, dry_run=False)
                existing_rules.add(fid)
                print(f"      → rule_id={rule['rule_id']} pattern={rule['pattern_type']} tag={rule['invalidation_tag']}")
            else:
                tombstone = {
                    "rule_id": f"FP-{_hex_ts()}-tombstone",
                    "pattern_type": "unverifiable_assumption",
                    "trigger_conditions": [],
                    "rejection_reason": rejection_reason[:200],
                    "vuln_type": vuln_type or "other",
                    "agent": "any",
                    "invalidation_tag": "unverifiable_assumption",
                    "confidence_threshold": 0.9,
                    "trust_level": 3,
                    "created_at": _now(),
                    "source_finding": fid,
                    "judge_outcome": "rejected",
                    "_bulk_import": True,
                    "_tombstone": True,
                }
                _write_rule(tombstone, PROJECT_FP_DIR, per_audit_fp_dir, dry_run=False)
                existing_rules.add(fid)

        processed += 1
        if not no_llm:
            time.sleep(0.3)  # avoid rate limiting

    return processed, skipped


def main():
    parser = argparse.ArgumentParser(description="Bulk FP autopsy — populate rejection rules corpus")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing")
    parser.add_argument("--audit", help="Process only a specific audit_id")
    parser.add_argument("--limit", type=int, default=None,
                        help="Max findings to process per audit (default: all)")
    parser.add_argument("--include-submitted-duplicates", action="store_true",
                        help="Also generate duplicate_pattern rules for submitted findings "
                             "confirmed as duplicates in the duplicate registry")
    parser.add_argument("--no-llm", action="store_true",
                        help="Generate rules from rejection reasons directly without calling Claude. "
                             "Rules have trust_level=2 (lower confidence than LLM-generated). "
                             "Use this to bootstrap the corpus instantly — then re-run without "
                             "--no-llm to upgrade high-value rules with LLM reasoning.")
    args = parser.parse_args()

    print("Bulk FP Autopsy — populating rejection rules corpus\n")
    if args.no_llm:
        print("  Mode: --no-llm (heuristic rules, no Claude API calls, trust_level=2)\n")

    rules_path = PROJECT_FP_DIR / "rejection_rules.jsonl"
    existing_rules = load_existing_rules(rules_path)
    print(f"Existing rules: {len(existing_rules)}")

    dup_registry = load_duplicate_registry() if args.include_submitted_duplicates else []
    if dup_registry:
        print(f"Duplicate registry: {len(dup_registry)} confirmed duplicates")

    audits = list_audits()
    if args.audit:
        audits = [a for a in audits if a.get("audit_id") == args.audit]
        if not audits:
            print(f"Audit '{args.audit}' not found")
            sys.exit(1)

    print(f"Audits to scan: {len(audits)}\n")

    client = None if args.no_llm else require_llm(skill="fp_autopsy")
    total_processed = 0
    total_skipped = 0

    for audit_meta in audits:
        audit_id = audit_meta.get("audit_id", "")
        registry_path = ROOT / "audits" / audit_id
        if not registry_path.exists():
            continue
        processed, skipped = process_audit(
            audit_id, registry_path, client, existing_rules,
            dry_run=args.dry_run, limit=args.limit,
            dup_registry=dup_registry if dup_registry else None,
            no_llm=args.no_llm,
        )
        total_processed += processed
        total_skipped += skipped

    print(f"\n{'[dry-run] ' if args.dry_run else ''}Done:")
    print(f"  Processed: {total_processed}")
    print(f"  Skipped (already had rule): {total_skipped}")
    if not args.dry_run:
        final_count = len(load_existing_rules(rules_path))
        print(f"  Total rules in corpus: {final_count}")
    print(f"\nNext: run `python scripts/fp_pattern_check.py --all` to apply rules to current findings")

    if not args.dry_run:
        try:
            import subprocess as _sp
            _sp.run([sys.executable, str(ROOT / "scripts" / "generate_status.py")],
                    capture_output=True, timeout=30)
        except Exception:
            pass


if __name__ == "__main__":
    main()
