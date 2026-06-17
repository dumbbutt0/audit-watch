#!/usr/bin/env python3
"""
deep_trace.py — Stage 0c of the deep invariant analysis pipeline.

Pairs high-suspicion invariants with dangerous interaction chains (by state variable
overlap), calls Claude to trace each pair, and routes results to:
  data/threads/promising_threads.jsonl  — verdict != DEAD_END
  data/threads/dead_ends.jsonl          — fully traced, no violation

Usage:
    python scripts/deep_trace.py
"""

from __future__ import annotations

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
INVARIANTS_DIR   = audit_path("data/invariants")
INTERACTIONS_DIR = audit_path("data/interactions")
THREADS_DIR      = audit_path("data/threads")
STATIC_JSON      = audit_path("output") / "static.json"
PROMPT_PATH      = ROOT / "prompts" / "deep_trace.md"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096
MAX_PAIRS = 20  # overridden by --max-pairs flag

CONTRACT_EXTENSIONS = {".sol", ".rs", ".vy"}


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _load_jsonl(path: Path) -> list[dict]:
    out = []
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass
    return out


def _append_jsonl(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _detect_contract_dir() -> Path | None:
    static = _load_json(STATIC_JSON)
    if isinstance(static, dict):
        cp = static.get("contract_path")
        if cp:
            p = ROOT / cp
            if p.exists():
                return p.parent if p.is_file() else p
    # Fallback: look for contracts/ dir
    for candidate in ["contracts", "src"]:
        p = ROOT / candidate
        if p.is_dir():
            return p
    return None


def _load_source_excerpts(functions: list[str], contract_dir: Path | None) -> dict[str, str]:
    if not contract_dir or not contract_dir.exists():
        return {}
    excerpts: dict[str, str] = {}
    all_sources: dict[str, str] = {}
    for ext in CONTRACT_EXTENSIONS:
        for p in contract_dir.rglob(f"*{ext}"):
            try:
                all_sources[p.name] = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                pass
    # Extract relevant function names (strip ContractName. prefix)
    func_names = set()
    for f in functions:
        parts = f.split(".")
        func_names.add(parts[-1])
    for fname, source in all_sources.items():
        lines = source.splitlines()
        for fn in func_names:
            for i, line in enumerate(lines):
                # Find function definition
                if fn in line and ("fn " in line or "function " in line):
                    start = max(0, i - 2)
                    end = min(len(lines), i + 40)
                    key = f"{fname}::{fn}"
                    excerpts[key] = "\n".join(lines[start:end])
    return excerpts


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


def _pair_score(inv: dict, chain: dict) -> float:
    return float(inv.get("suspicion_score", 0)) + float(chain.get("danger_score", 0))


def _has_overlap(inv: dict, chain: dict) -> bool:
    inv_vars = set(inv.get("state_variables_involved", []))
    chain_vars = set(chain.get("shared_state", []))
    if inv_vars & chain_vars:
        return True
    # Also check invariant_exposure in chain (it may reference the invariant_id)
    inv_id = inv.get("invariant_id", "")
    if inv_id and inv_id in chain.get("invariant_exposure", []):
        return True
    return False


def _run_soft_flag_pass(
    invariants: list[dict],
    dangerous: list[dict],
    system_prompt: str,
    contract_dir: Path | None,
    promising_path: Path,
    thread_counter: int,
    max_soft_pairs: int = 50,
) -> int:
    """Trace score-3 invariants against dangerous chains; mark results soft_flag=true."""
    if not invariants or not dangerous:
        return thread_counter
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("  --include-medium: no ANTHROPIC_API_KEY — soft-flag pass skipped")
        return thread_counter

    pairs: list[tuple[dict, dict]] = []
    for inv in invariants:
        for chain in dangerous:
            if _has_overlap(inv, chain):
                pairs.append((inv, chain))

    pairs.sort(key=lambda p: _pair_score(p[0], p[1]), reverse=True)
    pairs = pairs[:max_soft_pairs]

    if not pairs:
        return thread_counter

    print(f"\n  Soft-flag pass (score-3 invariants): {len(pairs)} pair(s)")

    for idx, (inv, chain) in enumerate(pairs, 1):
        thread_counter += 1
        thread_id = f"DT-S-{thread_counter:03d}"
        inv_id = inv.get("invariant_id", "?")
        chain_id = chain.get("chain_id", "?")
        print(f"\n  [soft {idx}/{len(pairs)}] Tracing {inv_id} × {chain_id} …", end="", flush=True)

        path_funcs = chain.get("path", [])
        excerpts = _load_source_excerpts(path_funcs, contract_dir)

        user_payload = {
            "thread_id": thread_id,
            "invariant": inv,
            "chain": chain,
            "source_excerpts": excerpts,
            "note": "soft-flag trace: suspicion_score=3, lower confidence threshold",
        }
        user_content = json.dumps(user_payload, ensure_ascii=False)

        try:
            raw = _call_claude(system_prompt, user_content)
        except Exception as e:
            print(f" ERROR: {e}")
            continue

        thread = _extract_json_object(raw)
        if not thread:
            print(" (no parseable JSON — skipping)")
            continue

        thread.setdefault("thread_id", thread_id)
        thread.setdefault("invariant_id", inv_id)
        thread.setdefault("chain_id", chain_id)
        thread["soft_flag"] = True
        thread["escalate"] = False  # soft threads are never auto-escalated

        verdict = thread.get("verdict", "UNKNOWN")
        print(f" {verdict} [soft]")

        if verdict != "DEAD_END":
            _append_jsonl(promising_path, thread)

    return thread_counter


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Deep trace: pair invariants with dangerous chains")
    parser.add_argument("--max-pairs", type=int, default=MAX_PAIRS,
                        help=f"Maximum invariant×chain pairs to trace (default: {MAX_PAIRS})")
    parser.add_argument("--include-medium", action="store_true",
                        help="Run a secondary pass against score-3 invariants (soft-flag threads, not auto-escalated)")
    args = parser.parse_args()
    max_pairs = args.max_pairs

    THREADS_DIR.mkdir(parents=True, exist_ok=True)
    promising_path = THREADS_DIR / "promising_threads.jsonl"
    dead_ends_path = THREADS_DIR / "dead_ends.jsonl"

    # Clear output files for a fresh run
    promising_path.write_text("")
    dead_ends_path.write_text("")

    print("Stage 0c — Deep Trace Analysis")

    invariants = _load_json(INVARIANTS_DIR / "high_suspicion.json")
    if not isinstance(invariants, list):
        print("  No high-suspicion invariants found. Run extract_invariants.py first.")
        return 0
    print(f"  Loaded {len(invariants)} high-suspicion invariant(s)")

    dangerous = _load_json(INTERACTIONS_DIR / "dangerous_chains.json")
    if not isinstance(dangerous, list):
        print("  No dangerous chains found. Run map_interactions.py first.")
        return 0
    print(f"  Loaded {len(dangerous)} dangerous chain(s)")

    # Build candidate pairs by state variable overlap
    pairs: list[tuple[dict, dict]] = []
    for inv in invariants:
        for chain in dangerous:
            if _has_overlap(inv, chain):
                pairs.append((inv, chain))

    # Sort by combined score descending, take top max_pairs as primary pass
    pairs.sort(key=lambda p: _pair_score(p[0], p[1]), reverse=True)
    top_pairs = pairs[:max_pairs]

    # Second pass: add CROSS_CONTRACT invariant pairs that didn't make the primary cut.
    # Cross-contract invariants are consistently underscored because they span files,
    # but they are disproportionately the ones that survive prior audit rounds.
    already_in_top = set(id(p) for p in top_pairs)
    cross_contract_extras = [
        p for p in pairs[max_pairs:]
        if p[0].get("category") == "CROSS_CONTRACT"
        and id(p) not in already_in_top
    ][:10]

    pairs = top_pairs + cross_contract_extras
    if cross_contract_extras:
        print(f"  Added {len(cross_contract_extras)} extra CROSS_CONTRACT pair(s) (second pass)")
    print(f"  Paired: {len(pairs)} invariant × chain combination(s) (primary {len(top_pairs)}, cross-contract bonus {len(cross_contract_extras)})")

    if not pairs:
        print("  No overlapping pairs found. Check state variable names in invariants vs chains.")
        return 0

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else (ROOT / "agents" / "deep_trace_agent.md").read_text(encoding="utf-8")
    contract_dir = _detect_contract_dir()

    verdict_counts: Counter = Counter()
    thread_counter = 0

    for idx, (inv, chain) in enumerate(pairs, 1):
        thread_counter += 1
        thread_id = f"DT-{thread_counter:03d}"
        inv_id = inv.get("invariant_id", "?")
        chain_id = chain.get("chain_id", "?")
        print(f"\n  [{idx}/{len(pairs)}] Tracing {inv_id} × {chain_id} …", end="", flush=True)

        # Load source excerpts for functions in the chain path
        path_funcs = chain.get("path", [])
        excerpts = _load_source_excerpts(path_funcs, contract_dir)

        user_payload = {
            "thread_id": thread_id,
            "invariant": inv,
            "chain": chain,
            "source_excerpts": excerpts,
        }
        user_content = json.dumps(user_payload, ensure_ascii=False)

        try:
            raw = _call_claude(system_prompt, user_content)
        except Exception as e:
            print(f" ERROR: {e}")
            continue

        thread = _extract_json_object(raw)
        if not thread:
            print(" (no parseable JSON — skipping)")
            continue

        # Ensure required fields
        thread.setdefault("thread_id", thread_id)
        thread.setdefault("invariant_id", inv_id)
        thread.setdefault("chain_id", chain_id)
        thread.setdefault("escalate", thread.get("verdict", "") != "DEAD_END")

        verdict = thread.get("verdict", "UNKNOWN")
        verdict_counts[verdict] += 1
        print(f" {verdict}")

        if verdict == "DEAD_END":
            _append_jsonl(dead_ends_path, thread)
        else:
            _append_jsonl(promising_path, thread)

    # Optional soft-flag pass (score-3 invariants)
    if args.include_medium:
        medium_path = INVARIANTS_DIR / "medium_suspicion.json"
        medium_invs = _load_json(medium_path)
        if isinstance(medium_invs, list) and medium_invs:
            print(f"\n  Loading {len(medium_invs)} medium-suspicion invariant(s) for soft-flag pass")
            thread_counter = _run_soft_flag_pass(
                medium_invs, dangerous, system_prompt, contract_dir,
                promising_path, thread_counter,
            )
        else:
            print("\n  --include-medium: no medium_suspicion.json found (run extract_invariants.py first)")

    # Summary
    promising = _load_jsonl(promising_path)
    dead = _load_jsonl(dead_ends_path)
    soft_count = sum(1 for t in promising if t.get("soft_flag"))
    print(f"\n  Results:")
    print(f"    Pairs traced: {len(pairs)}")
    print(f"    CRITICAL_THREAD: {verdict_counts.get('CRITICAL_THREAD', 0)}")
    print(f"    HIGH_THREAD:     {verdict_counts.get('HIGH_THREAD', 0)}")
    print(f"    MEDIUM_THREAD:   {verdict_counts.get('MEDIUM_THREAD', 0)}")
    print(f"    NEEDS_MORE_CONTEXT: {verdict_counts.get('NEEDS_MORE_CONTEXT', 0)}")
    print(f"    DEAD_END:        {verdict_counts.get('DEAD_END', 0)}")
    if soft_count:
        print(f"    Soft-flag (score-3): {soft_count}")
    print(f"\n  Promising threads: {len(promising)}  ({soft_count} soft-flag)")
    print(f"  Dead ends:         {len(dead)}")
    print(f"\n  Output files:")
    print(f"    {promising_path}")
    print(f"    {dead_ends_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
