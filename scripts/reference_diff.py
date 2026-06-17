#!/usr/bin/env python3
"""
reference_diff.py — Compare target contract functions against reference implementations.

For each key function category (liquidation, swap, borrow, etc.) in the audit target,
fetches the canonical reference implementation from kb/reference_implementations/<category>.json
and calls the Reference Diff Agent to identify security-relevant deviations.

Usage:
    python scripts/reference_diff.py --contract contracts/
    python scripts/reference_diff.py --contract contracts/ --category lending

Outputs:
    output/findings_reference_diff.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path
from llm_runtime import require_llm  # no-silent-fail: actionable message instead of credit spend/crash

ROOT           = Path(__file__).resolve().parent.parent
KB_DIR         = ROOT / "kb" / "reference_implementations"
OUTPUT_DIR     = audit_path("output")
AGENT_PROMPT   = ROOT / "agents" / "reference_diff_agent.md"
CONTEXT_FILE   = audit_path("output") / "findings_protocol_context.json"
STATIC_JSON    = audit_path("output") / "static.json"

MODEL      = "claude-sonnet-4-6"
MAX_TOKENS = 4096

CONTRACT_EXTENSIONS = {".sol", ".rs", ".vy"}

SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Informational": 4}


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _call_claude(system_prompt: str, user_content: str) -> str:
    client = require_llm(skill="reference_diff")
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return resp.content[0].text


def _extract_json_object(text: str) -> dict:
    text = text.strip()
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    if start == -1:
        return {}
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start: i + 1])
                except json.JSONDecodeError:
                    return {}
    return {}


def _detect_protocol_category() -> str:
    """Detect protocol category from protocol_context findings."""
    ctx = _load_json(CONTEXT_FILE)
    if isinstance(ctx, dict):
        findings = ctx.get("findings", [])
        for f in findings:
            desc = (f.get("description", "") + f.get("title", "")).lower()
            if any(kw in desc for kw in ("lending", "borrow", "liquidat", "collateral", "aave", "compound")):
                return "lending"
            if any(kw in desc for kw in ("swap", "amm", "pool", "liquidity", "uniswap", "curve", "dex")):
                return "dex"
            if any(kw in desc for kw in ("vault", "yield", "strategy", "erc4626", "erc-4626")):
                return "vault"
            if any(kw in desc for kw in ("staking", "stake", "reward", "emission")):
                return "staking"
    return "lending"  # Default to most-common critical type


def _extract_function_from_source(func_name: str, contract_dir: str) -> str:
    """Extract a named function from contract source files."""
    p = ROOT / contract_dir if not Path(contract_dir).is_absolute() else Path(contract_dir)
    candidates: list[Path] = []
    if p.is_file():
        candidates.append(p)
    elif p.is_dir():
        for ext in CONTRACT_EXTENSIONS:
            candidates.extend(p.rglob(f"*{ext}"))

    for path in candidates:
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = source.splitlines()
        for i, line in enumerate(lines):
            if func_name.lower() in line.lower() and (
                "function " in line or "fn " in line
            ):
                # Extract function body (up to 60 lines)
                start = max(0, i - 1)
                end = min(len(lines), i + 60)
                return "\n".join(lines[start:end])
    return ""


def _deviation_to_finding(dev: dict, ref_source: str, func_name: str, idx: int) -> dict | None:
    """Convert a RDIFF deviation into a standard finding."""
    classification = dev.get("classification", "intentional_safe")
    if classification == "intentional_safe":
        return None

    severity = dev.get("severity", "Medium")
    return {
        "id": f"RD-{idx:03d}",
        "title": f"Deviation from {ref_source} reference: {func_name} — {dev.get('type', 'unknown')}",
        "severity": severity,
        "vuln_type": "logic-error",
        "description": (
            f"The `{func_name}` implementation deviates from the {ref_source} reference "
            f"in a potentially security-relevant way.\n\n"
            f"Deviation type: {dev.get('type', '')}\n"
            f"Classification: {classification}\n\n"
            f"Reference implementation:\n```solidity\n{dev.get('reference_lines', '')}\n```\n\n"
            f"Target implementation:\n```solidity\n{dev.get('target_lines', '')}\n```\n\n"
            f"Rationale: {dev.get('rationale', '')}"
        ),
        "location": {
            "file": "target contract",
            "function": func_name,
            "line_start": None,
            "code_snippet": dev.get("target_lines", ""),
        },
        "impact": dev.get("attack_scenario", "Potential security impact from reference deviation"),
        "proof_of_concept": dev.get("attack_scenario", ""),
        "recommendation": (
            f"Review the deviation from {ref_source}'s `{func_name}` implementation. "
            f"The reference implementation includes this logic for a specific security reason. "
            f"If the deviation is intentional, document the rationale explicitly."
        ),
        "confidence": dev.get("confidence", "Medium"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Reference implementation diff analysis")
    parser.add_argument("--contract", default="contracts", help="Contract file or directory")
    parser.add_argument("--category", default=None,
                        help="Force protocol category (lending, dex, vault, staking)")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / "findings_reference_diff.json"

    print("Reference Implementation Diff Analysis")

    if not AGENT_PROMPT.exists():
        print(f"  Agent prompt not found: {AGENT_PROMPT}")
        out_file.write_text(json.dumps({"agent": "reference_diff", "findings": []}, indent=2))
        return 0

    category = args.category or _detect_protocol_category()
    print(f"  Protocol category: {category}")

    ref_file = KB_DIR / f"{category}.json"
    if not ref_file.exists():
        available = [f.stem for f in KB_DIR.glob("*.json")] if KB_DIR.exists() else []
        print(f"  No reference KB for category '{category}'. Available: {available}")
        out_file.write_text(json.dumps({"agent": "reference_diff", "findings": []}, indent=2))
        return 0

    ref_data = _load_json(ref_file)
    if not isinstance(ref_data, dict):
        print(f"  Could not load reference file: {ref_file}")
        out_file.write_text(json.dumps({"agent": "reference_diff", "findings": []}, indent=2))
        return 0

    reference_functions = ref_data.get("functions", [])
    ref_source_name = ref_data.get("category", category)
    print(f"  Reference functions: {len(reference_functions)}")

    system_prompt = AGENT_PROMPT.read_text(encoding="utf-8")
    all_findings = []
    finding_idx = 1

    for ref_func in reference_functions:
        func_name = ref_func.get("name", "")
        if not func_name:
            continue

        target_code = _extract_function_from_source(func_name, args.contract)
        if not target_code:
            # Try variant names
            for variant in [f"_{func_name}", func_name.lower(), func_name + "Internal"]:
                target_code = _extract_function_from_source(variant, args.contract)
                if target_code:
                    break

        if not target_code:
            print(f"  [{func_name}] not found in target — skipping")
            continue

        print(f"  Diffing {func_name} vs {ref_func.get('source', ref_source_name)} …", end="", flush=True)

        user_payload = json.dumps({
            "function_name": func_name,
            "reference_function": ref_func.get("code", ""),
            "reference_source": ref_func.get("source", ref_source_name),
            "target_function": target_code,
            "canonical_invariants": ref_func.get("canonical_invariants", []),
        }, ensure_ascii=False)

        try:
            raw = _call_claude(system_prompt, user_payload)
        except Exception as e:
            print(f" ERROR: {e}")
            continue

        result = _extract_json_object(raw)
        if not result:
            print(" (no parseable JSON)")
            continue

        deviations = result.get("deviations", [])
        actionable = [d for d in deviations if d.get("classification") != "intentional_safe"]
        print(f" {len(actionable)} actionable deviation(s)")

        for dev in actionable:
            finding = _deviation_to_finding(dev, ref_func.get("source", ref_source_name), func_name, finding_idx)
            if finding:
                all_findings.append(finding)
                finding_idx += 1

    # Sort by severity
    all_findings.sort(key=lambda f: SEVERITY_ORDER.get(f.get("severity", "Informational"), 99))

    out = {
        "agent": "reference_diff",
        "contract": args.contract,
        "findings": all_findings,
    }
    out_file.write_text(json.dumps(out, indent=2, ensure_ascii=False))

    print(f"\n  Findings from reference diff: {len(all_findings)}")
    print(f"  Output: {out_file}")
    import subprocess as _sp
    _sp.run([sys.executable, str(Path(__file__).resolve().parent / "generate_status.py")],
            check=False, capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
