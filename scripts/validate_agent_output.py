#!/usr/bin/env python3
"""
validate_agent_output.py

Zero-trust output validation gate. After each specialist agent writes its findings JSON,
this script validates:
1. JSON schema conformance against schema/findings_schema.json
2. Finding ID prefix matches the expected agent prefix
3. No shell metacharacters in text fields (injection artifact detection)
4. Severity values are in the allowed set
5. Finding count cap (>100 findings likely indicates hallucination)
6. Output size cap (per zero_trust_policy.json)

Called by report_generator.py before merging findings. Can also be run standalone.

Usage:
    python scripts/validate_agent_output.py output/findings_reentrancy.json
    python scripts/validate_agent_output.py output/  # validate all findings_*.json files
    python scripts/validate_agent_output.py output/ --strict  # exit 1 on any failure
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema not installed — schema validation skipped", file=sys.stderr)

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "findings_schema.json"
POLICY_PATH = Path(__file__).resolve().parent.parent / "config" / "zero_trust_policy.json"

ALLOWED_SEVERITIES = {"Critical", "High", "Medium", "Low", "Informational"}

AGENT_PREFIX_MAP = {
    "reentrancy":                  "RE-",
    "access_control":              "AC-",
    "arithmetic":                  "AR-",
    "oracle":                      "OR-",
    "flash_loan":                  "FL-",
    "logic":                       "LG-",
    "dos":                         "DS-",
    "snapshot":                    "SN-",
    "economic_attack":             "EA-",
    "token_integration":           "TI-",
    "cross_chain":                 "CC-",
    "upgrade_storage":             "US-",
    "protocol_context":            "PC-",
    "deep_trace":                  "DT-",
    "behavioral_state_analysis":   "BSA-",
    "semantic_guard":              "SG-",
    "erc4626":                     "V4-",
    "transient_storage":           "TS-",
    "compound_synthesis":          "CS-",
    "report_synthesis":            "RS-",
    "attacker_mindset":            "AM-",
    "supply_chain_check":          "SC-",
    # TON / FunC specialist bundle (language:ton — spawned by the ite-audit ton branch)
    "ton_sender_auth":             "TSA-",
    "ton_message_flow":            "TMF-",
    "ton_bounce_handling":         "TBH-",
    "ton_carry_value":             "TCV-",
    "ton_cell_parsing":            "TCP-",
    "ton_arithmetic":              "TAR-",
}

# Shell execution pattern — only flag Python code execution APIs that would never appear in
# legitimate audit text. Backtick and $() are excluded because they appear in Markdown
# inline code (e.g., `functionName`) and Solidity event logs respectively.
SHELL_META_RE = re.compile(r"__import__\s*\(|os\.system\s*\(|subprocess\.(?:run|call|Popen)\s*\(|shutil\.rmtree\s*\(|Path\s*\(.*\)\.unlink")

MAX_FINDINGS = 100

# No-silent-clear rule (2026-05 refinement): clearing safety-net code requires a written
# attacker-path disproof. Safety-net = code whose job is to protect the protocol.
SAFETY_NET_RE = re.compile(
    r"invariable|solvency|\bsort\b|quicksort|oracle|evaluate|\bprice\b|aggregator|"
    r"bridge|xdomain|season|sunrise|reseed|migrat|initiali[sz]|\binit\b|guard|"
    r"fundssafu|nonetflow|nooutflow|oneoutflow", re.I)
CLEARED_VERDICTS = {"cleared", "safe", "works_as_designed", "not_exploitable", "no_issue"}


def load_policy() -> dict:
    if POLICY_PATH.exists():
        return json.loads(POLICY_PATH.read_text())
    return {"max_agent_output_size_bytes": 524288, "forbidden_in_agent_output": []}


def _conf_to_float(conf) -> float:
    """Map a finding's confidence (float or Confirmed/High/Medium/Low/Speculative) to 0.0–1.0."""
    if isinstance(conf, (int, float)):
        return max(0.0, min(1.0, float(conf)))
    return {"confirmed": 0.95, "high": 0.85, "medium": 0.6, "low": 0.35,
            "speculative": 0.25}.get(str(conf or "").strip().lower(), 0.5)


def emit_specialist_events(agent_name: str, findings: list) -> int:
    """Reasoning-graph telemetry for a Step-2 specialist's findings: HYPOTHESIS_BORN per finding +
    EVIDENCE_ATTACHED per manifest ref. Fire-and-forget — no-ops unless VIZ_SESSION_ID is set, and
    NEVER raises (telemetry must not affect the validation gate). Returns hypotheses emitted.
    Mirrors the emit pattern in scripts/cross_agent_connector.py (Step 2.5)."""
    root = str(Path(__file__).resolve().parent.parent)
    if root not in sys.path:
        sys.path.insert(0, root)
    try:
        from viz.event_emitter import emit
    except Exception:
        return 0
    n = 0
    for f in findings:
        if not isinstance(f, dict) or not f.get("id"):
            continue
        fid = f["id"]
        try:
            loc = f.get("location", {}) or {}
            linked = [x for x in (loc.get("contract"), loc.get("file")) if x] if isinstance(loc, dict) else []
            emit("HYPOTHESIS_BORN", source_agent=agent_name or "specialist", target_node_id=fid,
                 payload={
                     "hypothesis_text": str(f.get("title", ""))[:200],
                     "severity_ceiling": f.get("severity", ""),
                     "exploit_class": f.get("vuln_type", ""),
                     "confidence": _conf_to_float(f.get("confidence")),
                     "linked_contracts": linked,
                 })
            n += 1
            # The finding's own cited evidence (location + PoC/description) — the primary evidence at
            # this pre-merge boundary (manifest_refs are attached later in the pipeline).
            loc_str = ""
            if isinstance(loc, dict):
                loc_str = loc.get("file", "") + (f":{loc.get('function')}" if loc.get("function") else "")
            else:
                loc_str = str(loc)
            evidence = (f.get("proof_of_concept") or f.get("description") or "")
            if loc_str or evidence:
                emit("EVIDENCE_ATTACHED", source_agent=agent_name or "specialist", target_node_id=None,
                     payload={"attached_to": fid, "evidence_type": "code_locus",
                              "content": (f"{loc_str} — {evidence}").strip(" —")[:200],
                              "source": loc_str, "confidence_delta": 0.0})
            for ev in (f.get("manifest_refs") or [])[:8]:
                emit("EVIDENCE_ATTACHED", source_agent=agent_name or "specialist", target_node_id=None,
                     payload={"attached_to": fid, "evidence_type": "manifest_ref",
                              "content": str(ev)[:200], "confidence_delta": 0.0})
        except Exception:
            continue
    return n


def validate_file(findings_path: Path, strict: bool = False) -> dict:
    result = {
        "file": str(findings_path),
        "valid": True,
        "errors": [],
        "warnings": [],
    }

    # Size check
    policy = load_policy()
    max_bytes = policy.get("max_agent_output_size_bytes", 524288)
    file_size = findings_path.stat().st_size if findings_path.exists() else 0
    if file_size > max_bytes:
        result["errors"].append(
            f"Output file size {file_size} bytes exceeds policy limit {max_bytes} bytes"
        )

    # Load JSON
    try:
        data = json.loads(findings_path.read_text())
    except json.JSONDecodeError as e:
        result["errors"].append(f"Invalid JSON: {e}")
        result["valid"] = False
        return result

    # JSON schema validation
    if HAS_JSONSCHEMA and SCHEMA_PATH.exists():
        schema = json.loads(SCHEMA_PATH.read_text())
        # Temporarily relax the agent enum to include new agents
        if "properties" in schema and "agent" in schema["properties"]:
            schema["properties"]["agent"]["enum"] = list(AGENT_PREFIX_MAP.keys())
        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as e:
            result["errors"].append(f"Schema violation: {e.message} at {list(e.path)}")

    agent_name = data.get("agent", "")
    findings = data.get("findings", [])

    # Finding count cap
    if len(findings) > MAX_FINDINGS:
        result["errors"].append(
            f"Finding count {len(findings)} exceeds cap of {MAX_FINDINGS} — possible hallucination"
        )

    # Per-finding checks
    expected_prefix = AGENT_PREFIX_MAP.get(agent_name)
    forbidden = policy.get("forbidden_in_agent_output", [])

    for i, finding in enumerate(findings):
        fid = finding.get("id", "")

        # ID prefix check
        if expected_prefix and not fid.startswith(expected_prefix):
            result["warnings"].append(
                f"Finding {i} ID '{fid}' does not match expected prefix '{expected_prefix}'"
            )

        # Severity check
        severity = finding.get("severity", "")
        if severity not in ALLOWED_SEVERITIES:
            result["errors"].append(
                f"Finding {fid}: invalid severity '{severity}'"
            )

        # No-silent-clear rule: a "cleared" verdict on safety-net code must carry a disproof.
        verdict = str(finding.get("verdict", "")).lower().replace(" ", "_")
        if verdict in CLEARED_VERDICTS:
            loc = finding.get("location", {}) or {}
            haystack = " ".join(str(x) for x in (
                loc.get("file", ""), loc.get("function", ""),
                finding.get("title", ""), finding.get("vuln_type", ""),
            ))
            if SAFETY_NET_RE.search(haystack) and not str(finding.get("disproof", "")).strip():
                result["errors"].append(
                    f"Finding {fid}: '{verdict}' verdict on safety-net code without a "
                    f"'disproof' field. Provide an attacker-path disproof or set "
                    f"verdict='unresolved_invariant' to route to human review."
                )
        # 'unresolved_invariant' is always a valid routing outcome (no disproof required).

        # Shell metacharacter scan in text fields
        for field in ("description", "recommendation", "proof_of_concept", "impact"):
            text = finding.get(field, "") or ""
            if SHELL_META_RE.search(text):
                result["errors"].append(
                    f"Finding {fid}: field '{field}' contains shell metacharacters — possible injection artifact"
                )

        # Policy-forbidden strings
        full_text = json.dumps(finding)
        for forbidden_str in forbidden:
            if forbidden_str in full_text:
                result["errors"].append(
                    f"Finding {fid}: contains forbidden string '{forbidden_str}'"
                )

    result["valid"] = len(result["errors"]) == 0
    result["finding_count"] = len(findings)
    result["agent"] = agent_name

    # Reasoning-graph telemetry (Step 2) — fire-and-forget; no-ops without VIZ_SESSION_ID; never
    # affects the validation outcome above. This is the Python ingest boundary for the 13 Markdown
    # specialists, which cannot emit themselves.
    emit_specialist_events(agent_name, findings)

    return result


def validate_directory(output_dir: Path, strict: bool = False) -> list[dict]:
    findings_files = sorted(output_dir.glob("findings_*.json"))
    if not findings_files:
        print(f"No findings_*.json files found in {output_dir}", file=sys.stderr)
        return []

    results = []
    for f in findings_files:
        results.append(validate_file(f, strict=strict))
    return results


def validate_triage_output(triage_dir: Path, strict: bool = False) -> dict:
    """Validate submit.jsonl entries for required fields.

    Checks that every entry in submit.jsonl has a non-empty, non-Unknown severity.
    Unusable entries cannot be submitted to any contest platform.
    """
    result = {
        "file": str(triage_dir / "submit.jsonl"),
        "valid": True,
        "errors": [],
        "warnings": [],
        "finding_count": 0,
    }

    submit_path = triage_dir / "submit.jsonl"
    if not submit_path.exists():
        result["warnings"].append("submit.jsonl not found — triage not yet run")
        return result

    REQUIRED_FIELDS = ["finding_id", "title", "triage_status", "recommended_severity"]
    VALID_SEVERITIES = {"critical", "high", "medium", "low", "qa", "informational"}

    entries: list[dict] = []
    for lineno, line in enumerate(submit_path.read_text().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            result["errors"].append(f"Line {lineno}: invalid JSON")

    result["finding_count"] = len(entries)

    for entry in entries:
        fid = entry.get("finding_id", f"<line {entries.index(entry)+1}>")

        for field in REQUIRED_FIELDS:
            if not entry.get(field):
                result["errors"].append(f"{fid}: missing required field '{field}'")

        sev = (entry.get("recommended_severity") or "").lower()
        if sev in ("", "unknown", "none"):
            result["errors"].append(
                f"{fid}: severity is '{sev}' — unusable for submission. "
                "Re-run triage or set severity manually."
            )
        elif sev not in VALID_SEVERITIES:
            result["warnings"].append(f"{fid}: unrecognised severity value '{sev}'")

        if not entry.get("decision_reason"):
            result["warnings"].append(f"{fid}: no decision_reason recorded")

    result["valid"] = len(result["errors"]) == 0
    return result


def main():
    parser = argparse.ArgumentParser(description="Agent output validation gate")
    parser.add_argument("target", help="Path to findings_*.json file, output/ directory, or data/triage/ directory")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any file fails validation")
    parser.add_argument("--json", dest="json_output", action="store_true", help="Output JSON")
    parser.add_argument("--triage", action="store_true", help="Validate triage JSONL outputs (submit.jsonl)")
    args = parser.parse_args()

    target = Path(args.target)

    if args.triage:
        triage_dir = target if target.is_dir() else target.parent
        results = [validate_triage_output(triage_dir, strict=args.strict)]
    elif target.is_dir():
        results = validate_directory(target, strict=args.strict)
    elif target.is_file():
        results = [validate_file(target, strict=args.strict)]
    else:
        print(f"Error: {target} does not exist", file=sys.stderr)
        sys.exit(1)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        any_failed = False
        for r in results:
            status = "✓" if r["valid"] else "✗"
            fc = r.get("finding_count", "?")
            print(f"{status} {r['file']} ({r.get('agent','?')}, {fc} findings)")
            for err in r.get("errors", []):
                print(f"    ERROR: {err}")
                any_failed = True
            for warn in r.get("warnings", []):
                print(f"    WARN:  {warn}")

        if any_failed:
            print("\nValidation failed. Fix errors before merging findings.")
            if args.strict:
                sys.exit(1)


if __name__ == "__main__":
    main()
