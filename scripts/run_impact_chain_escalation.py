#!/usr/bin/env python3
"""
run_impact_chain_escalation.py — Heuristic ICE enrichment pass.

Reads audits/<id>/output/merged_findings.json, searches for protocol consumers
of each finding's corrupted state using rg, and emits an ice block per finding.

IMPORTANT: This is a heuristic enrichment pass, not an authoritative verifier.
rg-based search misses indirect reads, interface calls, inheritance, delegatecall,
and generated accessors. consumer_search_confidence marks the reliability.
Findings with low confidence go to ice_manual_review.jsonl for human tracing.

Outputs:
  audits/<id>/output/findings_ice.json       — merged findings enriched with ice blocks
  audits/<id>/output/ice_manual_review.jsonl — findings needing human consumer tracing
  audits/<id>/output/ice_poc_required.jsonl  — findings needing PoC to reach next severity

Usage:
    python scripts/run_impact_chain_escalation.py [--audit-id <id>] [--contract-dir <path>]
"""

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

HIGH_RISK_VULN_TYPES = {
    "access-control", "oracle", "registry", "factory",
    "attestation", "cross-chain", "upgrade", "logic",
}

HIGH_CONSUMER_ACTIONS = {
    "deploy", "borrow", "withdraw", "liquidate", "authorize",
    "whitelist", "mint", "transfer", "governance", "approve",
}

SEVERITY_CEILING_BY_POC_LEVEL = {
    0: "Low",
    1: "Low",
    2: "Medium",
    3: "High",
    4: "High",
    5: "Critical",
}

SEVERITY_RANK = {
    "Critical": 5, "High": 4, "Medium": 3, "Low": 2, "Info": 1, "Informational": 1,
}

# Solidity consumer action patterns: (regex_pattern, action_type)
CONSUMER_PATTERNS = [
    (r'_mint\s*\(', "mint"),
    (r'\.mint\s*\(', "mint"),
    (r'\.transfer\s*\(', "transfer"),
    (r'\.call\s*\{value', "transfer"),
    (r'\.release\s*\(', "withdraw"),
    (r'_liquidat', "liquidate"),
    (r'\.liquidat', "liquidate"),
    (r'_borrow\s*\(', "borrow"),
    (r'\.borrow\s*\(', "borrow"),
    (r'grantRole\s*\(', "authorize"),
    (r'whitelist\[', "whitelist"),
    (r'new\s+\w+\s*\(', "deploy"),
    (r'queue\s*\(', "governance"),
    (r'\.approve\s*\(', "approve"),
    (r'getPrice\s*\(', "price_read"),
]

# ─────────────────────────────────────────────────────────────────────────────
# State identifier extraction
# ─────────────────────────────────────────────────────────────────────────────

def extract_state_identifier(finding: dict) -> str:
    """Extract the most likely state identifier from a finding's description."""
    desc = finding.get("description", "") + " " + finding.get("title", "")

    # Look for explicit storage variable patterns
    patterns = [
        r'`([a-zA-Z_][a-zA-Z0-9_]*\[[^\]]+\])`',   # mapping access
        r'`([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_]+)`',  # struct field
        r'`([a-zA-Z_][a-zA-Z0-9_]{3,})`',            # plain identifier (4+ chars)
        r'\b([a-zA-Z_][a-zA-Z0-9_]*(?:Map|State|Flag|Status|Manager|Registry|Price|Balance))\b',
    ]
    for pat in patterns:
        m = re.search(pat, desc)
        if m:
            candidate = m.group(1)
            # Skip common false positives
            if candidate.lower() not in {"false", "true", "this", "address", "bytes32", "uint256"}:
                return candidate

    # Fall back to vuln_type-based guess
    vuln = finding.get("vuln_type", "").lower()
    location_fn = finding.get("location", {}).get("function", "")
    if location_fn:
        return location_fn
    return vuln or "unknown"


def extract_corrupted_state_description(finding: dict) -> str:
    """Build a human-readable corrupted state description."""
    state_id = extract_state_identifier(finding)
    vuln = finding.get("vuln_type", "unknown")
    title = finding.get("title", "")

    if state_id and state_id != "unknown":
        return f"{state_id} — set by attacker via {vuln} in {finding.get('location', {}).get('function', 'unknown function')}"
    return f"corrupted state via {vuln} ({title[:60]})"


# ─────────────────────────────────────────────────────────────────────────────
# Consumer search
# ─────────────────────────────────────────────────────────────────────────────

def find_contract_dir() -> Path:
    """Find the most likely contracts directory."""
    candidates = [
        Path("contracts/fassets/contracts"),
        Path("contracts/fassets"),
        Path("contracts"),
        Path("."),
    ]
    for c in candidates:
        if c.exists() and any(c.rglob("*.sol")):
            return c
    return Path("contracts")


def rg_search(pattern: str, search_dir: Path, max_results: int = 20) -> list[dict]:
    """Run ripgrep for a pattern and return structured matches."""
    if not search_dir.exists():
        return []
    try:
        result = subprocess.run(
            ["rg", "--json", "-n", "--type", "sol", pattern, str(search_dir)],
            capture_output=True, text=True, timeout=10,
        )
        matches = []
        for line in result.stdout.splitlines():
            try:
                obj = json.loads(line)
                if obj.get("type") == "match":
                    data = obj["data"]
                    matches.append({
                        "file": data["path"]["text"],
                        "line": data["line_number"],
                        "text": data["lines"]["text"].strip(),
                    })
                    if len(matches) >= max_results:
                        break
            except (json.JSONDecodeError, KeyError):
                continue
        return matches
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def classify_consumer_action(match_text: str) -> str:
    """Classify the action type from a matched line of Solidity."""
    for pattern, action in CONSUMER_PATTERNS:
        if re.search(pattern, match_text):
            return action
    return "state_read"


def search_consumers(state_identifier: str, contract_dir: Path) -> tuple[list[dict], str]:
    """
    Search for consumers of a state identifier.
    Returns (consumers, confidence_level).
    """
    if state_identifier in ("unknown", "") or len(state_identifier) < 3:
        return [], "low"

    # Clean up the identifier for search
    search_term = re.sub(r'[\[\]\.{}()\s]', '', state_identifier)
    if len(search_term) < 3:
        return [], "low"

    matches = rg_search(search_term, contract_dir, max_results=30)
    match_count = len(matches)

    consumers = []
    seen_fns: set[str] = set()

    for m in matches:
        action = classify_consumer_action(m["text"])
        fn_key = f"{m['file']}:{action}"
        if fn_key in seen_fns:
            continue
        seen_fns.add(fn_key)

        fn_match = re.search(r'function\s+(\w+)', m["text"])
        fn_name = fn_match.group(1) if fn_match else f"line_{m['line']}"

        consumers.append({
            "file": m["file"],
            "function": fn_name,
            "action_type": action,
        })

    # Confidence assignment
    if match_count >= 5:
        confidence = "high"
    elif match_count >= 2:
        confidence = "medium"
    else:
        confidence = "low"

    # Downgrade confidence for internal/interface-typical patterns
    if any(s in state_identifier for s in ["Interface", "internal", "emit "]):
        confidence = "low"

    return consumers, confidence


def find_highest_consumer(consumers: list[dict]) -> str:
    """Find the most downstream/impactful consumer found."""
    high_actions = [c for c in consumers if c["action_type"] in HIGH_CONSUMER_ACTIONS]
    if high_actions:
        return f"{high_actions[0]['function']} in {Path(high_actions[0]['file']).name} ({high_actions[0]['action_type']})"
    if consumers:
        return f"{consumers[0]['function']} in {Path(consumers[0]['file']).name} ({consumers[0]['action_type']})"
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# PoC level derivation
# ─────────────────────────────────────────────────────────────────────────────

def derive_poc_level(finding: dict, consumers: list[dict]) -> int:
    """Estimate PoC level from finding data and consumer search results."""
    poc_text = (finding.get("proof_of_concept", "") or "").lower()
    has_poc = bool(poc_text.strip())
    has_high_consumer = any(c["action_type"] in HIGH_CONSUMER_ACTIONS for c in consumers)

    # Check existing runtime PoC data
    runtime_level = finding.get("runtime_poc_level", 0)
    if runtime_level:
        return int(runtime_level)

    if not has_poc:
        return 0
    if "level 5" in poc_text or "exact loss" in poc_text or "balance assert" in poc_text:
        return 5
    if "level 4" in poc_text or "financial impact" in poc_text:
        return 4
    if has_high_consumer and ("level 3" in poc_text or "end-to-end" in poc_text):
        return 3
    if has_high_consumer:
        return 2
    if consumers:
        return 2
    return 1


def derive_severity_ceiling(poc_level: int) -> str:
    return SEVERITY_CEILING_BY_POC_LEVEL.get(poc_level, "Low")


# ─────────────────────────────────────────────────────────────────────────────
# Impact text generation
# ─────────────────────────────────────────────────────────────────────────────

def derive_directly_proven(finding: dict, consumers: list[dict], poc_level: int) -> str:
    if poc_level == 0:
        return "root cause identified; no consumer traced yet"
    if poc_level == 1:
        return f"root cause confirmed: {extract_state_identifier(finding)} is attacker-controllable"
    if consumers:
        top = find_highest_consumer(consumers)
        if poc_level >= 3:
            return f"consumer {top} performs {consumers[0]['action_type']} with attacker-controlled state"
        return f"state flows to consumer {top}"
    return "root cause confirmed; consumer chain not yet traced"


def derive_plausible_escalation(finding: dict, consumers: list[dict], poc_level: int) -> str:
    severity = finding.get("severity", "").lower()
    if poc_level >= 3:
        return "financial quantification (exact loss amount) would establish Critical if proven"
    if consumers:
        high = [c for c in consumers if c["action_type"] in HIGH_CONSUMER_ACTIONS]
        if high:
            return (f"if {high[0]['function']} is reachable from attacker context, "
                    f"{high[0]['action_type']} could cause direct loss")
    if severity in ("high", "critical"):
        return f"claimed {severity} requires consumer trace to HIGH_CONSUMER_ACTION"
    return "impact limited to root cause without consumer confirmation"


def recommended_next_step(consumers: list[dict], poc_level: int) -> str:
    if poc_level >= 5:
        return "submit — impact fully proven"
    if poc_level >= 3:
        return "quantify financial loss; write balance assertion in PoC to reach Level 5"
    if consumers:
        high = [c for c in consumers if c["action_type"] in HIGH_CONSUMER_ACTIONS]
        if high:
            return f"build PoC that calls {high[0]['function']} through the full call chain to confirm {high[0]['action_type']}"
        return f"trace from {consumers[0]['function']} to a HIGH_CONSUMER_ACTION (mint/transfer/liquidate)"
    return "manually trace consumers via agents/impact_chain_escalation.md — rg search found no matches"


# ─────────────────────────────────────────────────────────────────────────────
# Defenses and objections stubs
# ─────────────────────────────────────────────────────────────────────────────

def build_defenses_stub(finding: dict) -> list[dict]:
    """Build a placeholder defenses list to be filled by manual review."""
    vuln = finding.get("vuln_type", "")
    stubs = []
    if "access" in vuln or "auth" in vuln:
        stubs.append({"defense": "onlyOwner/onlyGovernance modifier", "checked": False, "result": "not checked — manual review required"})
    if "reentran" in vuln:
        stubs.append({"defense": "ReentrancyGuard (nonReentrant modifier)", "checked": False, "result": "not checked — verify diamond storage slot"})
    if "oracle" in vuln or "price" in vuln:
        stubs.append({"defense": "maxTrustedPriceAgeSeconds staleness check", "checked": False, "result": "not checked"})
    if not stubs:
        stubs.append({"defense": "generic access control", "checked": False, "result": "not checked — manual review required"})
    return stubs


def build_objections_stub(finding: dict) -> list[dict]:
    """Build placeholder triager objections to be pre-empted by human reviewer."""
    vuln = finding.get("vuln_type", "").lower()
    severity = finding.get("severity", "").lower()
    objections = []

    if severity in ("high", "critical"):
        objections.append({
            "objection": "impact is speculative without running PoC",
            "evidence_against": "see proof_of_concept field; consumer chain traced via ICE",
            "still_weak": True,
        })
    if "front" in (finding.get("description", "") or "").lower():
        objections.append({
            "objection": "frontrunning requires mempool visibility not available on all validators",
            "evidence_against": "Flare has 2s block time; mempool is public; economically viable",
            "still_weak": False,
        })
    if not objections:
        objections.append({
            "objection": "finding may be known or out-of-scope",
            "evidence_against": "v1.3.0 delta code not in prior Zellic/OpenZeppelin audits",
            "still_weak": True,
        })
    return objections


# ─────────────────────────────────────────────────────────────────────────────
# ICE block builder
# ─────────────────────────────────────────────────────────────────────────────

def build_ice_block(finding: dict, contract_dir: Path) -> dict:
    """Build the full ICE block for a single finding."""
    fid = finding.get("id", "?")
    vuln_type = (finding.get("vuln_type") or "").lower()

    corrupted_state = extract_corrupted_state_description(finding)
    state_id = extract_state_identifier(finding)

    consumers, confidence = search_consumers(state_id, contract_dir)

    has_high_consumer = any(c["action_type"] in HIGH_CONSUMER_ACTIONS for c in consumers)
    no_consumers = len(consumers) == 0

    poc_level = derive_poc_level(finding, consumers)
    severity_ceiling = derive_severity_ceiling(poc_level)
    highest_consumer = find_highest_consumer(consumers)
    directly_proven = derive_directly_proven(finding, consumers, poc_level)
    plausible_esc = derive_plausible_escalation(finding, consumers, poc_level)
    next_step = recommended_next_step(consumers, poc_level)

    # Hold assignment: no consumers found + high-risk vuln type
    hold = no_consumers and vuln_type in HIGH_RISK_VULN_TYPES

    # Manual review: low confidence OR hold
    needs_manual_review = confidence == "low" or hold

    ice = {
        "corrupted_state": corrupted_state,
        "consumers_found": consumers,
        "consumer_search_confidence": confidence,
        "highest_consumer_reached": highest_consumer,
        "poc_level_achieved": poc_level,
        "directly_proven_impact": directly_proven,
        "plausible_escalation": plausible_esc,
        "severity_ceiling": severity_ceiling,
        "recommended_next_poc_step": next_step,
        "hold": hold,
        "needs_manual_review": needs_manual_review,
        "triager_objections": build_objections_stub(finding),
        "defenses_checked": build_defenses_stub(finding),
        "manual_override": {
            "enabled": False,
            "reason": "",
            "reviewer": "",
            "new_severity_ceiling": "",
        },
    }

    return ice


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract-dir", default=None, help="Path to contracts directory")
    args = parser.parse_args(argv)

    output_dir = audit_path("output")
    merged_path = output_dir / "merged_findings.json"

    if not merged_path.exists():
        print(f"[error] {merged_path} not found — run report_generator.py first")
        return 1

    merged = json.loads(merged_path.read_text())
    findings = merged.get("findings", [])
    print(f"Impact Chain Escalation — heuristic enrichment pass")
    print(f"  Loaded {len(findings)} findings from merged_findings.json")

    contract_dir = Path(args.contract_dir) if args.contract_dir else find_contract_dir()
    print(f"  Contract search path: {contract_dir}")
    if not contract_dir.exists():
        print(f"  [warn] Contract dir {contract_dir} not found — consumer search will return empty results")

    # Check rg is available
    try:
        subprocess.run(["rg", "--version"], capture_output=True, check=True, timeout=5)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("  [warn] ripgrep (rg) not found — consumer search disabled; all findings get confidence=low")
        contract_dir = Path("/nonexistent")

    enriched_findings = []
    manual_review = []
    poc_required = []

    for finding in findings:
        fid = finding.get("id", "?")
        ice = build_ice_block(finding, contract_dir)
        enriched = {**finding, "ice": ice}
        enriched_findings.append(enriched)

        if ice["needs_manual_review"]:
            manual_review.append({"finding_id": fid, "title": finding.get("title", ""), "ice": ice})

        severity = ice["severity_ceiling"]
        if (ice["poc_level_achieved"] < 3
                and SEVERITY_RANK.get(severity, 0) >= SEVERITY_RANK.get("Medium", 0)):
            poc_required.append({"finding_id": fid, "title": finding.get("title", ""), "ice": ice})

        hold_marker = " [HOLD]" if ice["hold"] else ""
        review_marker = " [MANUAL]" if ice["needs_manual_review"] else ""
        print(f"  {fid}: conf={ice['consumer_search_confidence']}, "
              f"consumers={len(ice['consumers_found'])}, "
              f"poc_level={ice['poc_level_achieved']}, "
              f"ceiling={ice['severity_ceiling']}"
              f"{hold_marker}{review_marker}")

    # Write outputs
    ice_path = output_dir / "findings_ice.json"
    ice_path.write_text(json.dumps({"findings": enriched_findings}, indent=2))

    manual_path = output_dir / "ice_manual_review.jsonl"
    with manual_path.open("w") as fh:
        for rec in manual_review:
            fh.write(json.dumps(rec) + "\n")

    poc_path = output_dir / "ice_poc_required.jsonl"
    with poc_path.open("w") as fh:
        for rec in poc_required:
            fh.write(json.dumps(rec) + "\n")

    # Summary
    held = sum(1 for f in enriched_findings if f["ice"]["hold"])
    print(f"\n  ICE enrichment complete:")
    print(f"    {len(enriched_findings)} findings enriched → output/findings_ice.json")
    print(f"    {len(manual_review)} need manual consumer tracing → output/ice_manual_review.jsonl")
    print(f"    {len(poc_required)} need PoC to reach next severity → output/ice_poc_required.jsonl")
    print(f"    {held} on hold (high-risk vuln type, no consumers found)")

    if manual_review:
        print(f"\n  Manual review queue (spawn agents/impact_chain_escalation.md for each):")
        for rec in manual_review[:5]:
            print(f"    {rec['finding_id']}: {rec['title'][:60]}")
        if len(manual_review) > 5:
            print(f"    ... and {len(manual_review) - 5} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
