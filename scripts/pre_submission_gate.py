#!/usr/bin/env python3
"""
pre_submission_gate.py — 8-gate pre-submission reality filter.

Run as Step 3.7 — after multi_pass_confirm.py, before triage_findings.py.
Evaluates each finding against 8 structural validity gates and assigns
hard invalidation tags to findings that fail. Tagged findings are hard-
rejected in triage without consuming API budget.

Gates:
  1. Reachability   — can a realistic attacker trigger the vulnerable path?
  2. State Realism  — can required state actually exist?
  3. Privilege      — does attack require admin/compromised key?
  4. Defense        — are existing defenses bypassed or is coverage full?
  5. Economics      — is there real profit/damage, not just theoretical?
  6. PoC            — is proof required and present for Critical/High?
  7. Severity       — does judge simulation agree with the severity claim?
  8. Duplicate      — is this a known duplicate or FP pattern?

Usage:
    python scripts/pre_submission_gate.py [--all] [--finding-id <ID>] [--strict]
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

OUTPUT_DIR  = audit_path("output")
TRIAGE_DIR  = audit_path("data/triage")
EXPLOIT_DIR = audit_path("data/exploitability")
POC_DIR     = audit_path("data/runtime_poc")
JUDGE_DIR   = audit_path("data/judge_simulation")
DUP_DIR     = audit_path("data/duplicates")
FP_DIR      = audit_path("data/fp_autopsies")
PROJECT_ROOT = Path(__file__).resolve().parent.parent

ADMIN_KEYWORDS = ["admin", "emission_manager", "emergency_admin", "owner", "governor", "guardian"]
UNTRUSTED_ADMIN_MARKERS = [
    "untrusted admin", "admin is untrusted", "admin can be compromised",
    "compromised admin", "malicious admin",
]
IMPOSSIBLE_STATE_KEYWORDS = [
    "100% of supply", "requires price == 0", "oracle down", "all users must",
    "never happens in practice", "all liquidity removed", "zero liquidity",
    "requires mainnet fork", "impossible in practice",
]
COMPROMISED_KEY_KEYWORDS = [
    "private key", "compromised signer", "leaked key", "stolen key",
    "compromised private", "key compromise",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# Data loaders (all non-fatal on missing files)
# ─────────────────────────────────────────────────────────────────────────────

def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _load_jsonl_by_id(path: Path, id_field: str = "finding_id") -> dict[str, dict]:
    return {r[id_field]: r for r in _load_jsonl(path) if id_field in r}


def load_all_findings() -> list[dict]:
    seen_ids: set[str] = set()
    findings: list[dict] = []

    # Prefer merged_findings.json (already deduplicated by report_generator)
    merged_path = OUTPUT_DIR / "merged_findings.json"
    if merged_path.exists():
        try:
            merged = json.loads(merged_path.read_text())
            for f in merged.get("findings", []):
                fid = f.get("id", "")
                if fid and fid not in seen_ids:
                    seen_ids.add(fid)
                    findings.append(f)
            if findings:
                return findings
        except json.JSONDecodeError:
            pass

    # Fall back to individual agent output files (deduplicate by ID)
    for path in sorted(OUTPUT_DIR.glob("findings_*.json")):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if data.get("agent") == "protocol_context":
            continue
        for f in data.get("findings", []):
            fid = f.get("id", "")
            if fid and fid not in seen_ids:
                seen_ids.add(fid)
                findings.append(f)
    return findings


def load_defense_map() -> dict[str, dict]:
    path = OUTPUT_DIR / "defense_map.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        return data.get("defense_mappings", {})
    except json.JSONDecodeError:
        return {}


def load_exploit_models() -> dict[str, dict]:
    return _load_jsonl_by_id(EXPLOIT_DIR / "models.jsonl")


def _poc_level_to_int(level) -> int:
    if isinstance(level, int):
        return level
    if isinstance(level, str):
        m = re.match(r'L(\d+)', level.upper())
        if m:
            return int(m.group(1))
    return 0


def load_poc_results() -> dict[str, dict]:
    """Load PoC results from both data/runtime_poc and data/poc_queue."""
    results: dict[str, dict] = {}

    # 1. Load from runtime_poc/results.jsonl (Claude-generated PoCs)
    for r in _load_jsonl(POC_DIR / "results.jsonl"):
        fid = r.get("finding_id", "")
        if fid:
            r["runtime_level"] = _poc_level_to_int(r.get("runtime_level", 0))
            results[fid] = r

    # 2. Merge from poc_queue individual result files (fork PoCs, run_poc_tests.py)
    poc_queue_dir = audit_path("data/poc_queue")
    for result_file in poc_queue_dir.glob("*_result.json"):
        try:
            d = json.loads(result_file.read_text())
            fid = d.get("finding_id", "")
            if not fid:
                continue
            d["runtime_level"] = _poc_level_to_int(d.get("runtime_level", d.get("poc_level", 0)))
            # Prefer proved status: a proved poc_queue result wins over non-proved runtime_poc
            if fid not in results or (
                d.get("status") == "proved" and results[fid].get("status") != "proved"
            ):
                results[fid] = d
        except (json.JSONDecodeError, OSError):
            pass

    # 3. Also check poc_queue/results.jsonl for any additional entries
    for r in _load_jsonl(poc_queue_dir / "results.jsonl"):
        fid = r.get("finding_id", "")
        if fid and fid not in results:
            r["runtime_level"] = _poc_level_to_int(r.get("runtime_level", r.get("poc_level", 0)))
            results[fid] = r

    return results


def load_judge_results() -> dict[str, dict]:
    return _load_jsonl_by_id(JUDGE_DIR / "results.jsonl")


def load_duplicate_risks() -> dict[str, dict]:
    return _load_jsonl_by_id(DUP_DIR / "risk.jsonl")


def load_triage_records() -> dict[str, dict]:
    records: dict[str, dict] = {}
    for fname in ["submit.jsonl", "poc_required.jsonl", "downgraded.jsonl", "rejected.jsonl"]:
        for rec in _load_jsonl(TRIAGE_DIR / fname):
            fid = rec.get("finding_id", "")
            if fid and fid not in records:
                records[fid] = rec
    return records


def load_fp_pattern_results() -> dict[str, dict]:
    path = FP_DIR / "pattern_check_results.jsonl"
    return _load_jsonl_by_id(path)


def load_cross_audit_submissions() -> list[dict]:
    """Load submitted findings from all audits for cross-audit duplicate check."""
    submissions = []
    audits_dir = PROJECT_ROOT / "audits"
    if not audits_dir.exists():
        return submissions
    for submit_path in audits_dir.rglob("data/triage/submit.jsonl"):
        # Skip the current audit
        if str(audit_path("data/triage")) in str(submit_path):
            continue
        submissions.extend(_load_jsonl(submit_path))
    return submissions


def load_duplicate_registry() -> list[dict]:
    """Load project-level registry of confirmed duplicate findings (+ auto-promoted entries)."""
    out: list[dict] = []
    for path in (PROJECT_ROOT / "data" / "duplicate_registry.jsonl",
                 PROJECT_ROOT / "data" / "auto_promoted_duplicate_registry.jsonl"):
        if path.exists():
            out += [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return out


def _registry_overlap(finding: dict, registry: list[dict]) -> tuple[float, str | None]:
    """Score a finding against the duplicate registry. Returns (score, registry_id)."""
    vt = finding.get("vuln_type", "")
    text = (finding.get("title", "") + " " + finding.get("description", "")).lower()
    best_score, best_id = 0.0, None
    for entry in registry:
        score = 0.0
        if entry.get("vuln_type") == vt:
            score += 0.4
        sig_tokens = entry.get("root_cause_signature", "").lower().split()
        hits = sum(1 for t in sig_tokens if len(t) > 3 and t in text)
        score += min(0.5, hits * 0.1)
        if best_score < score:
            best_score, best_id = score, entry.get("registry_id")
    return best_score, best_id


# ─────────────────────────────────────────────────────────────────────────────
# Gate result builder
# ─────────────────────────────────────────────────────────────────────────────

def _gate(n: int, name: str, verdict: str, reason: str = "", tag: str | None = None) -> dict:
    return {"gate": n, "name": name, "verdict": verdict, "reason": reason, "tag": tag}


# ─────────────────────────────────────────────────────────────────────────────
# Individual gates
# ─────────────────────────────────────────────────────────────────────────────

def gate_reachability(finding: dict, exploit: dict | None) -> dict:
    if not exploit:
        return _gate(1, "reachability", "WARN", "No exploitability model found — cannot assess reachability")

    can_trigger = exploit.get("can_trigger", True)
    blocked_by_auth = exploit.get("blocked_by_auth", False)

    if not can_trigger and blocked_by_auth:
        return _gate(1, "reachability", "FAIL",
                     "blocked_by_auth=True and can_trigger=False — no reachable attack path",
                     "non_exploitable")

    if not can_trigger:
        return _gate(1, "reachability", "WARN",
                     "can_trigger=False — attack path requires further verification")

    return _gate(1, "reachability", "PASS")


def gate_state_realism(finding: dict, triage: dict | None) -> dict:
    desc = (
        finding.get("description", "") + " " +
        (finding.get("impact", "") or "") + " " +
        (finding.get("proof_of_concept", "") or "")
    ).lower()

    for kw in IMPOSSIBLE_STATE_KEYWORDS:
        if kw.lower() in desc:
            return _gate(2, "state_realism", "FAIL",
                         f"Description contains impossible-state indicator: '{kw}'",
                         "impossible_state")

    # Check preconditions from triage record
    if triage:
        preconditions = triage.get("attacker_model", {}).get("required_preconditions", [])
        for pre in preconditions:
            pre_lower = pre.lower()
            if any(imp in pre_lower for imp in ["impossible", "never", "0% chance", "theoretical only"]):
                return _gate(2, "state_realism", "FAIL",
                             f"Precondition is self-described as impossible: '{pre}'",
                             "impossible_state")

    # Warn on timing-dependent preconditions without PoC
    poc = (finding.get("proof_of_concept", "") or "").lower()
    timing_keywords = ["same block", "next block", "specific epoch", "exact block"]
    if any(kw in desc for kw in timing_keywords) and not poc.strip():
        return _gate(2, "state_realism", "WARN",
                     "Timing-dependent precondition without PoC evidence")

    # Warn on high assumption count — brittle exploit chains are likely FPs
    preconditions = []
    if triage:
        preconditions = triage.get("attacker_model", {}).get("required_preconditions", [])
    assumption_count = finding.get("assumption_count", len(preconditions))
    if assumption_count >= 4:
        return _gate(2, "state_realism", "WARN",
                     f"High assumption count ({assumption_count}) — exploit requires many preconditions not guaranteed by protocol")

    return _gate(2, "state_realism", "PASS")


def gate_privilege(finding: dict, exploit: dict | None, triage: dict | None) -> dict:
    desc = (finding.get("description", "") + " " + (finding.get("impact", "") or "")).lower()
    poc = (finding.get("proof_of_concept", "") or "").lower()

    # Hard reject: requires compromised key
    if any(kw in desc for kw in COMPROMISED_KEY_KEYWORDS):
        return _gate(3, "privilege", "FAIL",
                     "Attack requires a compromised private key — not a protocol vulnerability",
                     "requires_compromised_key")

    # Check attacker type from exploit model or triage
    attacker_type = ""
    realistic = True
    if exploit:
        attacker_type = exploit.get("attacker", {}).get("type", "")
        realistic = exploit.get("attacker", {}).get("realistic", True)
    if triage:
        attacker_type = attacker_type or triage.get("attacker_model", {}).get("attacker_type", "")
        realistic = realistic and triage.get("attacker_model", {}).get("realistic", True)

    if attacker_type == "admin" and not realistic:
        # Check for untrusted-admin argument
        has_untrusted = any(m in desc or m in poc for m in UNTRUSTED_ADMIN_MARKERS)
        if not has_untrusted:
            return _gate(3, "privilege", "FAIL",
                         "Admin-only attacker with realistic=False and no untrusted-admin justification",
                         "admin_only")

    # Warn if admin keyword present without explicit justification
    if any(kw in desc for kw in ADMIN_KEYWORDS) and attacker_type == "admin":
        has_untrusted = any(m in desc or m in poc for m in UNTRUSTED_ADMIN_MARKERS)
        if not has_untrusted:
            return _gate(3, "privilege", "WARN",
                         "Admin-role attacker — confirm untrusted-admin scenario is explicitly argued")

    return _gate(3, "privilege", "PASS")


def gate_defense(finding: dict, defense_map: dict[str, dict]) -> dict:
    fid = finding.get("id", "")
    mapping = defense_map.get(fid)

    if not mapping:
        return _gate(4, "defense", "PASS",
                     "No defense mapping found — cannot assess (defense_mapper.py may not have run)")

    coverage = mapping.get("coverage", "unknown")
    evasion = mapping.get("evasion_path", "")
    defenses = [d["modifier"] for d in mapping.get("applicable_defenses", [])]

    if coverage == "full" and not evasion:
        return _gate(4, "defense", "FAIL",
                     f"Full defense coverage via {defenses} with no evasion path identified",
                     "already_guarded")

    if coverage == "full" and evasion:
        return _gate(4, "defense", "WARN",
                     f"Full coverage via {defenses} but evasion path found: {evasion[:80]}")

    if coverage == "partial":
        return _gate(4, "defense", "WARN",
                     f"Partial defense coverage via {defenses} — verify the gap is exploitable")

    return _gate(4, "defense", "PASS")


def _parse_eth_amounts(text: str) -> list[float]:
    matches = re.findall(r'(\d+\.?\d*)\s*(?:ETH|eth)', text)
    return [float(m) for m in matches]


def gate_economics(finding: dict, exploit: dict | None, triage: dict | None) -> dict:
    # Check profit_or_damage from exploit model (hard signal — explicit model says no profit)
    exploit_no_profit = False
    if exploit:
        pod = exploit.get("profit_or_damage", {})
        if isinstance(pod, dict):
            pod_type = pod.get("type", "")
            bounded = pod.get("bounded", False)
            if pod_type == "none" and bounded:
                exploit_no_profit = True

    # Check triage loss_type — "none" is also the fallback default, so only FAIL when
    # the exploit model also agrees, or the record is an explicit parse-error fallback.
    triage_no_profit = False
    if triage:
        loss_type = triage.get("impact", {}).get("loss_type", "")
        is_parse_error = triage.get("_parse_error", False)
        if loss_type == "none" and is_parse_error:
            # Parse-error fallback + loss_type=none → WARN, not FAIL (too uncertain)
            triage_no_profit = False
        elif loss_type == "none":
            triage_no_profit = True  # may be meaningful or may be a default

    # FAIL only when exploit model explicitly confirms no profit (strong signal)
    if exploit_no_profit:
        return _gate(5, "economics", "FAIL",
                     "Exploitability model reports no profit/damage possible (type=none, bounded=True)",
                     "no_profitability")

    # WARN when triage says loss_type=none but we have no exploit model to confirm
    if triage_no_profit and not exploit:
        return _gate(5, "economics", "WARN",
                     "Triage loss_type=none — verify that real economic impact exists (no exploit model found)")

    # Heuristic: parse ETH amounts from description + PoC
    desc = (finding.get("description", "") + " " + (finding.get("proof_of_concept", "") or ""))
    cost_match = re.findall(r'cost[s]?\s+(?:of\s+)?(\d+\.?\d*)\s*ETH', desc, re.IGNORECASE)
    gain_match = re.findall(r'(?:gain|profit|steal|extract|drain)\s+(\d+\.?\d*)\s*ETH', desc, re.IGNORECASE)

    if cost_match and gain_match:
        max_cost = max(float(x) for x in cost_match)
        max_gain = max(float(x) for x in gain_match)
        if max_cost > max_gain * 1.5:
            return _gate(5, "economics", "FAIL",
                         f"Attack cost ({max_cost} ETH) exceeds estimated profit ({max_gain} ETH)",
                         "no_profitability")
        if max_cost > max_gain * 0.8:
            return _gate(5, "economics", "WARN",
                         f"Attack cost ({max_cost} ETH) close to estimated profit ({max_gain} ETH)")

    # Good signals
    vuln_type = finding.get("vuln_type", "")
    good_types = {"reentrancy", "flash-loan", "oracle-manipulation", "price-manipulation"}
    if vuln_type in good_types:
        return _gate(5, "economics", "PASS")

    if triage:
        loss_type = triage.get("impact", {}).get("loss_type", "")
        if loss_type in ("fund_loss", "insolvency", "permanent_lock"):
            return _gate(5, "economics", "PASS")

    return _gate(5, "economics", "PASS")


def gate_poc(finding: dict, poc_results: dict[str, dict], triage: dict | None) -> dict:
    severity = finding.get("severity", "")
    fid = finding.get("id", "")

    if severity not in ("Critical", "High"):
        return _gate(6, "poc", "PASS", "PoC not required for Medium/Low findings")

    poc_result = poc_results.get(fid, {})
    poc_level = poc_result.get("runtime_level", poc_result.get("level", 0))
    poc_status = poc_result.get("status", "")

    needs_poc = False
    if triage:
        needs_poc = triage.get("exploitability", {}).get("needs_poc", False)

    if needs_poc and poc_level == 0:
        return _gate(6, "poc", "FAIL",
                     f"{severity} finding requires PoC but none exists (needs_poc=True, level=0)")

    if poc_level > 0 and poc_status not in ("proved", "passed"):
        return _gate(6, "poc", "WARN",
                     f"PoC exists at level {poc_level} but status is '{poc_status}' (not proved)")

    if poc_level >= 2 and poc_status in ("proved", "passed"):
        return _gate(6, "poc", "PASS", f"PoC proved at level {poc_level}")

    return _gate(6, "poc", "PASS")


def gate_severity_realism(finding: dict, judge: dict | None, triage: dict | None) -> dict:
    if not judge:
        return _gate(7, "severity_realism", "WARN", "No judge simulation found — cannot assess severity realism")

    outcome = judge.get("predicted_outcome", "")
    confidence = judge.get("confidence", 0)

    if outcome == "rejected" and confidence >= 4:
        objection = judge.get("strongest_objection", "")[:80]
        return _gate(7, "severity_realism", "FAIL",
                     f"Judge simulation predicted rejection (confidence={confidence}): {objection}")

    if outcome in ("accepted_downgraded",):
        reason = (judge.get("severity_downgrade_reasons") or [""])[0][:60]
        return _gate(7, "severity_realism", "WARN",
                     f"Judge simulation predicted severity downgrade: {reason}")

    if outcome in ("duplicate_risk",):
        return _gate(7, "severity_realism", "WARN",
                     "Judge simulation flagged high duplicate risk")

    return _gate(7, "severity_realism", "PASS")


def _function_overlap(a: str, b: str) -> bool:
    """Check if two function name strings share at least one meaningful token."""
    tokens_a = set(re.findall(r'[a-z][A-Z]?[a-z]*', a))
    tokens_b = set(re.findall(r'[a-z][A-Z]?[a-z]*', b))
    common = tokens_a & tokens_b
    meaningful = {t for t in common if len(t) > 3}
    return len(meaningful) >= 1


def gate_duplicate(
    finding: dict,
    dup_risks: dict[str, dict],
    fp_patterns: dict[str, dict],
    cross_audit_submissions: list[dict],
    dup_registry: list[dict] | None = None,
) -> dict:
    fid = finding.get("id", "")
    vuln_type = finding.get("vuln_type", "")
    fn_name = finding.get("location", {}).get("function", "")

    # Registry check — confirmed duplicates from past audits
    if dup_registry:
        reg_score, reg_id = _registry_overlap(finding, dup_registry)
        if reg_score >= 0.85:
            return _gate(8, "duplicate", "FAIL",
                         f"Registry match {reg_id}: known duplicate pattern (score={reg_score:.2f})",
                         "duplicate_pattern")
        if reg_score >= 0.70:
            return _gate(8, "duplicate", "WARN",
                         f"Registry near-match {reg_id}: review before submitting (score={reg_score:.2f})")

    # FP pattern check result
    fp_result = fp_patterns.get(fid, {})
    if fp_result.get("recommended_action") == "reject":
        top_rule = (fp_result.get("matching_rules") or [{}])[0]
        sim = top_rule.get("similarity", 0)
        reason = top_rule.get("rejection_reason", "")[:60]
        return _gate(8, "duplicate", "FAIL",
                     f"FP pattern match (similarity={sim:.2f}): {reason}",
                     "duplicate_pattern")

    # Duplicate risk from estimate_duplicate_risk
    dup = dup_risks.get(fid, {})
    if dup.get("duplicate_risk") == "high" or dup.get("score") == "high":
        return _gate(8, "duplicate", "FAIL",
                     "Estimated duplicate risk is HIGH — likely same root cause as another finding",
                     "duplicate_finding")

    # Cross-audit lightweight scan
    for past in cross_audit_submissions:
        past_vuln = past.get("finding", {}).get("vuln_type", "") or past.get("vuln_type", "")
        past_fn = (
            past.get("finding", {}).get("location", {}).get("function", "") or
            past.get("location", {}).get("function", "")
        )
        if past_vuln == vuln_type and fn_name and past_fn and _function_overlap(fn_name, past_fn):
            return _gate(8, "duplicate", "WARN",
                         f"Cross-audit match: same vuln_type '{vuln_type}' + overlapping function '{past_fn}'")

    # Warn on high FP pattern similarity (below auto-reject threshold)
    if fp_result.get("top_similarity", 0) > 0.6:
        sim = fp_result["top_similarity"]
        return _gate(8, "duplicate", "WARN",
                     f"FP pattern similarity={sim:.2f} — review for known-invalid pattern")

    # Warn on medium duplicate risk
    if dup.get("duplicate_risk") == "medium" or dup.get("score") == "medium":
        return _gate(8, "duplicate", "WARN",
                     "Estimated duplicate risk is MEDIUM — verify root cause is distinct")

    return _gate(8, "duplicate", "PASS")


# ─────────────────────────────────────────────────────────────────────────────
# Overall verdict
# ─────────────────────────────────────────────────────────────────────────────

def compute_overall_verdict(gate_results: list[dict]) -> dict:
    fails = [g for g in gate_results if g["verdict"] == "FAIL"]
    warns = [g for g in gate_results if g["verdict"] == "WARN"]
    tags = [g["tag"] for g in fails if g.get("tag")]

    if fails:
        verdict = "REJECT"
    elif len(warns) >= 3:
        verdict = "HUMAN_REVIEW"
    else:
        verdict = "PASS"

    return {
        "verdict": verdict,
        "fail_count": len(fails),
        "warn_count": len(warns),
        "invalidation_tags": tags,
        "blocking_issues": [g["reason"] for g in fails] + (
            [g["reason"] for g in warns] if verdict == "HUMAN_REVIEW" else []
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Evaluate one finding
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_finding(
    finding: dict,
    defense_map: dict[str, dict],
    exploit_models: dict[str, dict],
    poc_results: dict[str, dict],
    judge_results: dict[str, dict],
    dup_risks: dict[str, dict],
    triage_records: dict[str, dict],
    fp_patterns: dict[str, dict],
    cross_audit: list[dict],
    dup_registry: list[dict] | None = None,
) -> dict:
    fid = finding.get("id", "?")
    exploit = exploit_models.get(fid)
    poc = poc_results.get(fid)
    judge = judge_results.get(fid)
    triage = triage_records.get(fid)

    gates = [
        gate_reachability(finding, exploit),
        gate_state_realism(finding, triage),
        gate_privilege(finding, exploit, triage),
        gate_defense(finding, defense_map),
        gate_economics(finding, exploit, triage),
        gate_poc(finding, poc_results, triage),
        gate_severity_realism(finding, judge, triage),
        gate_duplicate(finding, dup_risks, fp_patterns, cross_audit, dup_registry),
    ]

    overall = compute_overall_verdict(gates)

    return {
        "finding_id": fid,
        "severity": finding.get("severity", ""),
        "vuln_type": finding.get("vuln_type", ""),
        "gate_results": gates,
        "overall_verdict": overall["verdict"],
        "fail_count": overall["fail_count"],
        "warn_count": overall["warn_count"],
        "invalidation_tags": overall["invalidation_tags"],
        "blocking_issues": overall["blocking_issues"],
        "evaluated_at": _now(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="8-gate pre-submission reality filter")
    parser.add_argument("--all", action="store_true", help="Evaluate all findings")
    parser.add_argument("--finding-id", help="Evaluate a specific finding")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any finding is REJECT")
    parser.add_argument("--mode", choices=["pre-triage", "post-triage"], default="pre-triage")
    args = parser.parse_args()

    print("Pre-Submission Gate — Step 3.7\n")

    findings = load_all_findings()
    if args.finding_id:
        findings = [f for f in findings if f.get("id") == args.finding_id]

    if not findings:
        print("  No findings to evaluate")
        return

    print(f"  Loading pipeline data...")
    defense_map    = load_defense_map()
    exploit_models = load_exploit_models()
    poc_results    = load_poc_results()
    judge_results  = load_judge_results()
    dup_risks      = load_duplicate_risks()
    triage_records = load_triage_records()
    fp_patterns    = load_fp_pattern_results()
    cross_audit    = load_cross_audit_submissions()
    dup_registry   = load_duplicate_registry()

    if defense_map:
        print(f"  Defense map: {len(defense_map)} entries")
    else:
        print("  [warn] No defense map found — Gate 4 will PASS by default")
    if cross_audit:
        print(f"  Cross-audit submissions: {len(cross_audit)} entries")
    if dup_registry:
        print(f"  Duplicate registry: {len(dup_registry)} confirmed duplicates")

    results: list[dict] = []
    reject_count = 0
    human_review_count = 0
    pass_count = 0

    print(f"\n  Evaluating {len(findings)} findings...\n")

    for finding in findings:
        result = evaluate_finding(
            finding, defense_map, exploit_models, poc_results,
            judge_results, dup_risks, triage_records, fp_patterns, cross_audit,
            dup_registry
        )
        results.append(result)

        fid = result["finding_id"]
        verdict = result["overall_verdict"]
        tags = result["invalidation_tags"]

        if verdict == "REJECT":
            reject_count += 1
            print(f"  [REJECT] {fid} — tags: {tags}")
            for issue in result["blocking_issues"]:
                print(f"           • {issue}")
        elif verdict == "HUMAN_REVIEW":
            human_review_count += 1
            print(f"  [REVIEW] {fid} — {result['warn_count']} warnings")
        else:
            pass_count += 1

    # ── Hermes: emit gate decisions ──────────────────────────────────────────
    try:
        from scripts.emit_hermes_event import emit_hermes as _h_emit
        from audit_context import get_audit_meta as _get_meta
        _gate_audit_id = _get_meta().get("audit_id", "")
        for _gr in results:
            _h_emit("gate_decision", {
                "finding_id": _gr["finding_id"],
                "overall_verdict": _gr["overall_verdict"],
                "invalidation_tags": _gr.get("invalidation_tags", []),
                "fail_count": _gr.get("fail_count", 0),
                "warn_count": _gr.get("warn_count", 0),
                "audit_id": _gate_audit_id,
            })
    except Exception:
        pass

    # Write output
    TRIAGE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = TRIAGE_DIR / "gate_results.jsonl"
    out_path.write_text("\n".join(json.dumps(r) for r in results) + ("\n" if results else ""))

    print(f"\n  Results: {pass_count} PASS, {human_review_count} HUMAN_REVIEW, {reject_count} REJECT")
    print(f"  Wrote {out_path}")

    # Run generate_status.py
    import subprocess
    status_script = Path(__file__).resolve().parent / "generate_status.py"
    if status_script.exists():
        subprocess.run([sys.executable, str(status_script)], check=False)

    if args.strict and reject_count > 0:
        print(f"\n  [strict] {reject_count} finding(s) failed gates — exiting 1")
        sys.exit(1)


if __name__ == "__main__":
    main()
