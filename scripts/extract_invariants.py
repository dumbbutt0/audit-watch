#!/usr/bin/env python3
"""
extract_invariants.py — Stage 0a of the deep invariant analysis pipeline.

Reads contract source and static analysis output, calls Claude to extract
all protocol invariants, and writes:
  data/invariants/protocol_invariants.json  — full invariant array
  data/invariants/high_suspicion.json       — suspicion_score >= 4 only

Usage:
    python scripts/extract_invariants.py --contract <path_or_dir>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path
from llm_runtime import require_llm  # no-silent-fail: actionable message instead of credit spend/crash

ROOT = Path(__file__).resolve().parent.parent
INVARIANTS_DIR = audit_path("data/invariants")
STATIC_JSON    = audit_path("output") / "static.json"
PROMPT_PATH    = ROOT / "prompts" / "invariant_extractor.md"

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


def _load_static() -> dict:
    try:
        return json.loads(STATIC_JSON.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _call_claude(system_prompt: str, user_content: str) -> str:
    client = require_llm(skill="deep_analysis")
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return response.content[0].text


def _extract_json_array(text: str) -> list:
    # Try direct parse first
    text = text.strip()
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass
    # Find first [ ... ] block
    start = text.find("[")
    if start == -1:
        return []
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    return []
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract protocol invariants via Claude")
    parser.add_argument("--contract", required=True, help="Path to contract file or directory")
    args = parser.parse_args()

    contract_path = Path(args.contract)
    if not contract_path.exists():
        print(f"Error: contract path not found: {contract_path}", file=sys.stderr)
        return 1

    INVARIANTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Stage 0a — Protocol Invariant Extraction")
    print(f"  Contract: {contract_path}")

    sources = _load_contract_sources(contract_path)
    if not sources:
        print(f"  Warning: no contract source files found in {contract_path}")
        return 1
    print(f"  Loaded {len(sources)} source file(s)")

    static_data = _load_static()
    if static_data:
        print(f"  Loaded static analysis ({len(static_data.get('functions', []))} functions)")
    else:
        print("  No static.json found — proceeding with source only")

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    user_payload = {
        "contract_source": sources,
        "static_analysis": static_data,
    }
    user_content = json.dumps(user_payload, ensure_ascii=False)

    print(f"  Calling {MODEL} (max_tokens={MAX_TOKENS}) …")
    try:
        raw = _call_claude(system_prompt, user_content)
    except Exception as e:
        print(f"  Claude API error: {e}", file=sys.stderr)
        return 1

    invariants = _extract_json_array(raw)
    if not invariants:
        print("  Warning: Claude returned no parseable invariants")
        invariants = []

    # Sort by suspicion_score descending
    invariants.sort(key=lambda x: x.get("suspicion_score", 0), reverse=True)

    # Write full output
    out_all = INVARIANTS_DIR / "protocol_invariants.json"
    out_all.write_text(json.dumps(invariants, indent=2, ensure_ascii=False))

    # Write high-suspicion subset (score >= 4)
    high = [inv for inv in invariants if inv.get("suspicion_score", 0) >= 4]
    out_high = INVARIANTS_DIR / "high_suspicion.json"
    out_high.write_text(json.dumps(high, indent=2, ensure_ascii=False))

    # Write medium-suspicion subset (score == 3) for the soft-flag pass in deep_trace.py
    medium = [inv for inv in invariants if inv.get("suspicion_score", 0) == 3]
    out_medium = INVARIANTS_DIR / "medium_suspicion.json"
    out_medium.write_text(json.dumps(medium, indent=2, ensure_ascii=False))

    # Summary
    print(f"\n  Results:")
    print(f"    Total invariants extracted: {len(invariants)}")

    category_counts = Counter(inv.get("category", "UNKNOWN") for inv in invariants)
    for cat, count in sorted(category_counts.items()):
        print(f"    {cat}: {count}")

    score_counts = Counter(inv.get("suspicion_score", 0) for inv in invariants)
    print(f"\n    By suspicion score:")
    for score in range(5, 0, -1):
        n = score_counts.get(score, 0)
        bar = "█" * n
        print(f"      Score {score}: {n:3d}  {bar}")

    print(f"\n    High-suspicion (score >= 4):   {len(high)}")
    print(f"    Medium-suspicion (score == 3): {len(medium)}")
    print(f"\n  Output files:")
    print(f"    {out_all}")
    print(f"    {out_high}")
    print(f"    {out_medium}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
