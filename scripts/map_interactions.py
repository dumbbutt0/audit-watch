#!/usr/bin/env python3
"""
map_interactions.py — Stage 0b of the deep invariant analysis pipeline.

Reads contract source, static analysis, and protocol invariants, then calls
Claude to build a complete cross-system interaction map. Writes:
  data/interactions/call_graph.json       — full interaction map
  data/interactions/dangerous_chains.json — danger_score >= 4 chains only

Usage:
    python scripts/map_interactions.py --contract <path_or_dir>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path
from llm_runtime import require_llm  # no-silent-fail: actionable message instead of credit spend/crash

ROOT = Path(__file__).resolve().parent.parent
INTERACTIONS_DIR = audit_path("data/interactions")
INVARIANTS_DIR   = audit_path("data/invariants")
STATIC_JSON      = audit_path("output") / "static.json"
PROMPT_PATH      = ROOT / "prompts" / "interaction_mapper.md"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8192

CONTRACT_EXTENSIONS = {".sol", ".rs", ".vy"}


def _load_contract_sources(contract_path: Path) -> dict[str, str]:
    sources: dict[str, str] = {}
    if contract_path.is_file():
        if contract_path.suffix in CONTRACT_EXTENSIONS:
            sources[str(contract_path)] = contract_path.read_text(encoding="utf-8", errors="replace")
    elif contract_path.is_dir():
        for ext in CONTRACT_EXTENSIONS:
            for p in sorted(contract_path.rglob(f"*{ext}")):
                sources[str(p.resolve().relative_to(ROOT))] = p.read_text(encoding="utf-8", errors="replace")
    return sources


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _call_claude(system_prompt: str, user_content: str) -> str:
    client = require_llm(skill="deep_analysis")
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return response.content[0].text


def _extract_json_object(text: str) -> dict:
    text = text.strip()
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    # Find first { ... } block
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
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    return {}
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Map cross-system interactions via Claude")
    parser.add_argument("--contract", required=True, help="Path to contract file or directory")
    args = parser.parse_args()

    contract_path = Path(args.contract)
    if not contract_path.exists():
        print(f"Error: contract path not found: {contract_path}", file=sys.stderr)
        return 1

    INTERACTIONS_DIR.mkdir(parents=True, exist_ok=True)

    print("Stage 0b — Cross-System Interaction Mapping")
    print(f"  Contract: {contract_path}")

    sources = _load_contract_sources(contract_path)
    if not sources:
        print(f"  Warning: no contract source files found in {contract_path}")
        return 1
    print(f"  Loaded {len(sources)} source file(s)")

    static_data = _load_json(STATIC_JSON) or {}
    if static_data:
        print(f"  Loaded static analysis")
    else:
        print("  No static.json found — proceeding without it")

    invariants = _load_json(INVARIANTS_DIR / "protocol_invariants.json") or []
    print(f"  Loaded {len(invariants)} protocol invariant(s)")

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    user_payload = {
        "contract_source": sources,
        "static_analysis": static_data,
        "invariants": invariants,
    }
    user_content = json.dumps(user_payload, ensure_ascii=False)

    print(f"  Calling {MODEL} (max_tokens={MAX_TOKENS}) …")
    try:
        raw = _call_claude(system_prompt, user_content)
    except Exception as e:
        print(f"  Claude API error: {e}", file=sys.stderr)
        return 1

    result = _extract_json_object(raw)
    if not result:
        print("  Warning: Claude returned no parseable interaction map")
        result = {"call_graph": [], "interaction_chains": [], "trust_boundary_crossings": []}

    # Ensure required keys
    result.setdefault("call_graph", [])
    result.setdefault("interaction_chains", [])
    result.setdefault("trust_boundary_crossings", [])

    # Sort chains by danger_score descending
    chains = result["interaction_chains"]
    chains.sort(key=lambda x: x.get("danger_score", 0), reverse=True)

    # Write full output
    out_full = INTERACTIONS_DIR / "call_graph.json"
    out_full.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    # Write dangerous chains subset (danger_score >= 4)
    dangerous = [c for c in chains if c.get("danger_score", 0) >= 4]
    out_dangerous = INTERACTIONS_DIR / "dangerous_chains.json"
    out_dangerous.write_text(json.dumps(dangerous, indent=2, ensure_ascii=False))

    # Summary
    total_chains = len(chains)
    total_crossings = len(result["trust_boundary_crossings"])
    total_calls = len(result["call_graph"])

    print(f"\n  Results:")
    print(f"    Call graph edges: {total_calls}")
    print(f"    Interaction chains found: {total_chains}")
    print(f"    Dangerous chains (score >= 4): {len(dangerous)}")
    print(f"    Trust boundary crossings: {total_crossings}")

    if dangerous:
        print(f"\n    Top dangerous chains:")
        for chain in dangerous[:5]:
            cid = chain.get("chain_id", "?")
            score = chain.get("danger_score", "?")
            depth = chain.get("depth", "?")
            path = " → ".join(chain.get("path", []))[:80]
            print(f"      [{cid}] score={score} depth={depth}  {path}")

    print(f"\n  Output files:")
    print(f"    {out_full}")
    print(f"    {out_dangerous}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
