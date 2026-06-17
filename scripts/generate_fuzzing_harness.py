#!/usr/bin/env python3
"""
generate_fuzzing_harness.py — Stage 0d: Auto-generate Echidna fuzzing harnesses.

Converts ACCOUNTING and SOLVENCY invariants (suspicion_score >= 3) into
Echidna-compatible Solidity property-based test contracts.

Optionally runs Echidna if installed. Any falsified property becomes a thread
in data/threads/promising_threads.jsonl.

Usage:
    python scripts/generate_fuzzing_harness.py --contract contracts/
    python scripts/generate_fuzzing_harness.py --contract contracts/ --run-echidna
    python scripts/generate_fuzzing_harness.py --dry-run   # generate without running

Outputs:
    pocs/<audit_id>/fuzzing/echidna_properties.sol   — combined harness
    pocs/<audit_id>/fuzzing/Fuzz_<ID>.sol            — per-invariant harness
    data/threads/fuzzing_threads.jsonl               — falsified invariants as threads
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, get_active_audit_id
from llm_runtime import require_llm  # no-silent-fail: actionable message instead of credit spend/crash

ROOT           = Path(__file__).resolve().parent.parent
INVARIANTS_DIR = audit_path("data/invariants")
THREADS_DIR    = audit_path("data/threads")
AGENT_PROMPT   = ROOT / "agents" / "fuzzing_harness_writer.md"

MODEL      = "claude-sonnet-4-6"
MAX_TOKENS = 4096

FUZZ_CATEGORIES = {"ACCOUNTING", "SOLVENCY"}
MIN_SUSPICION   = 3

CONTRACT_EXTENSIONS = {".sol", ".rs", ".vy"}


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _append_jsonl(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _call_claude(system_prompt: str, user_content: str) -> str:
    client = require_llm(skill="deep_analysis")
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


def _load_contract_source(contract_path: str) -> dict[str, str]:
    sources: dict[str, str] = {}
    p = ROOT / contract_path if not Path(contract_path).is_absolute() else Path(contract_path)
    if p.is_file():
        sources[p.name] = p.read_text(encoding="utf-8", errors="replace")
    elif p.is_dir():
        for ext in CONTRACT_EXTENSIONS:
            for f in p.rglob(f"*{ext}"):
                try:
                    sources[f.name] = f.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    pass
    return sources


def _detect_contract_name(sources: dict[str, str]) -> str:
    for fname, src in sources.items():
        m = re.search(r'contract\s+(\w+)', src)
        if m:
            return m.group(1)
    return "TargetContract"


def _run_echidna(harness_path: Path, config_path: Path | None) -> list[str]:
    """Run Echidna on the harness. Returns list of falsified property names."""
    cmd = ["echidna", str(harness_path)]
    if config_path and config_path.exists():
        cmd += ["--config", str(config_path)]
    cmd += ["--format", "json", "--timeout", "60"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        falsified = []
        for line in result.stdout.splitlines():
            try:
                obj = json.loads(line)
                if obj.get("kind") == "property" and obj.get("status") == "falsified":
                    falsified.append(obj.get("name", "unknown"))
            except json.JSONDecodeError:
                pass
        return falsified
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Echidna fuzzing harnesses from invariants")
    parser.add_argument("--contract", default="contracts",
                        help="Path to contract file or directory")
    parser.add_argument("--run-echidna", action="store_true",
                        help="Run Echidna after generating harnesses")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be generated without writing files")
    args = parser.parse_args()

    print("Stage 0d — Fuzzing Harness Generation")

    THREADS_DIR.mkdir(parents=True, exist_ok=True)

    invariants = _load_json(INVARIANTS_DIR / "protocol_invariants.json")
    if not isinstance(invariants, list):
        print("  No invariants found. Run extract_invariants.py first.")
        return 0

    candidates = [
        inv for inv in invariants
        if inv.get("category") in FUZZ_CATEGORIES
        and float(inv.get("suspicion_score", 0)) >= MIN_SUSPICION
    ]
    print(f"  Candidates for fuzzing: {len(candidates)} (category in {FUZZ_CATEGORIES}, score >= {MIN_SUSPICION})")

    if not candidates:
        print("  No suitable invariants found.")
        return 0

    sources = _load_contract_source(args.contract)
    contract_name = _detect_contract_name(sources)
    source_excerpt = "\n\n".join(
        f"// {fname}\n{src[:2000]}" for fname, src in list(sources.items())[:3]
    )

    if not AGENT_PROMPT.exists():
        print(f"  Agent prompt not found: {AGENT_PROMPT}")
        return 1
    system_prompt = AGENT_PROMPT.read_text(encoding="utf-8")

    # Determine output directory
    audit_id = get_active_audit_id() if hasattr(sys.modules.get("audit_context"), "get_active_audit_id") else "default"
    try:
        from audit_context import get_active_audit_id as _gai
        audit_id = _gai()
    except Exception:
        audit_id = "default"

    fuzz_dir = ROOT / "pocs" / audit_id / "fuzzing"
    if not args.dry_run:
        fuzz_dir.mkdir(parents=True, exist_ok=True)

    generated_harnesses = []
    fuzzing_threads_path = THREADS_DIR / "fuzzing_threads.jsonl"

    for i, inv in enumerate(candidates, 1):
        inv_id = inv.get("invariant_id", f"INV-{i}")
        print(f"\n  [{i}/{len(candidates)}] {inv_id}: {inv.get('statement', '')[:60]} …", end="", flush=True)

        user_payload = json.dumps({
            "invariant": inv,
            "source_excerpts": {"contract": source_excerpt[:3000]},
            "contract_name": contract_name,
            "setup_hints": f"Deploy {contract_name} with minimal constructor args",
        }, ensure_ascii=False)

        try:
            raw = _call_claude(system_prompt, user_payload)
        except Exception as e:
            print(f" ERROR: {e}")
            continue

        result = _extract_json_object(raw)
        if not result or result.get("error"):
            reason = result.get("error", "parse fail") if result else "parse fail"
            print(f" SKIP ({reason})")
            continue

        solidity_code = result.get("solidity_code", "")
        harness_name = result.get("harness_contract", f"Fuzz_{inv_id.replace('-', '')}")
        if not solidity_code:
            print(" SKIP (no solidity_code)")
            continue

        harness_path = fuzz_dir / f"{harness_name}.sol"
        if not args.dry_run:
            harness_path.write_text(solidity_code, encoding="utf-8")
        generated_harnesses.append(harness_path)
        print(f" generated {harness_name}")

        if args.run_echidna and not args.dry_run:
            print(f"    Running Echidna on {harness_name} …", end="", flush=True)
            config_path = ROOT / "echidna.yaml"
            falsified = _run_echidna(harness_path, config_path)
            if falsified:
                print(f" FALSIFIED: {falsified}")
                for prop in falsified:
                    thread = {
                        "thread_id": f"FZ-{i:03d}",
                        "invariant_id": inv_id,
                        "chain_id": f"FUZZ-{inv_id}",
                        "verdict": "HIGH_THREAD",
                        "entry_conditions": f"Echidna falsified property {prop}",
                        "hop_traces": [],
                        "violation_path": [f"Echidna counterexample for {prop}"],
                        "profit_or_damage": f"Invariant '{inv.get('statement', '')}' violated",
                        "escalation_angles": [
                            f"Trace the counterexample sequence manually",
                            f"Check if the violation is reachable from a public entry point",
                        ],
                        "escalate": True,
                        "source": "echidna",
                    }
                    _append_jsonl(fuzzing_threads_path, thread)
            else:
                print(" no violations found")

    # Write combined harness
    if generated_harnesses and not args.dry_run:
        combined_path = fuzz_dir / "echidna_properties.sol"
        parts = ["// Combined fuzzing harness — auto-generated by generate_fuzzing_harness.py\n"]
        for hp in generated_harnesses:
            parts.append(f"\n// ─── {hp.name} ───\n")
            parts.append(hp.read_text(encoding="utf-8"))
        combined_path.write_text("\n".join(parts), encoding="utf-8")
        print(f"\n  Combined harness: {combined_path}")

    print(f"\n  Harnesses generated: {len(generated_harnesses)}")
    if args.dry_run:
        print("  [dry-run] No files written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
