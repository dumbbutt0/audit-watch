#!/usr/bin/env python3
"""
multi_tx_trace.py — Multi-transaction state machine vulnerability tracer.

Reads STATE_MACHINE invariants from data/invariants/protocol_invariants.json,
identifies two-step function pairs where an attacker can manipulate state between
steps, calls Claude with agents/multi_tx_agent.md for each candidate, and appends
MT-NNN threads to data/threads/promising_threads.jsonl.

Usage:
    python scripts/multi_tx_trace.py
    python scripts/multi_tx_trace.py --max-candidates 15
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
AGENTS_DIR = ROOT / "agents"
INVARIANTS_FILE = audit_path("data/invariants") / "protocol_invariants.json"
HIGH_SUSPICION_FILE = audit_path("data/invariants") / "high_suspicion.json"
STATIC_JSON = audit_path("output") / "static.json"
CONTEXT_JSON = audit_path("output") / "findings_protocol_context.json"
THREADS_FILE = audit_path("data/threads") / "promising_threads.jsonl"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096

CONTRACT_EXTENSIONS = {".sol", ".rs", ".vy"}

# State-machine patterns that suggest a two-step vulnerability
TWO_STEP_PAIRS = [
    ("request", "claim"),
    ("request", "finalize"),
    ("propose", "execute"),
    ("queue", "execute"),
    ("submit", "execute"),
    ("approve", "execute"),
    ("lock", "unlock"),
    ("deposit", "withdraw"),
    ("stake", "unstake"),
    ("commit", "reveal"),
    ("initiate", "complete"),
    ("schedule", "execute"),
]


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _load_source_for_functions(func_names: list[str]) -> dict[str, str]:
    excerpts: dict[str, str] = {}
    names = {f.split(".")[-1] for f in func_names if f}

    candidates: list[Path] = []
    for d in ("contracts", "src"):
        p = ROOT / d
        if p.is_dir():
            for ext in CONTRACT_EXTENSIONS:
                candidates.extend(p.rglob(f"*{ext}"))

    static = _load_json(STATIC_JSON)
    if isinstance(static, dict) and static.get("contract_path"):
        cp = ROOT / static["contract_path"]
        if cp.is_file():
            candidates.append(cp)

    for path in candidates:
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = source.splitlines()
        for fn in names:
            for i, line in enumerate(lines):
                if fn in line and ("function " in line or "fn " in line or "def " in line):
                    start = max(0, i - 1)
                    end = min(len(lines), i + 50)
                    excerpts[f"{path.name}::{fn}"] = "\n".join(lines[start:end])
    return excerpts


def _score_invariant(inv: dict) -> int:
    """Higher score = more promising multi-tx candidate."""
    score = inv.get("suspicion_score", 0)
    category = inv.get("category", "")
    if category == "STATE_MACHINE":
        score += 4
    # Two-step mutating function pair check
    funcs = [f.lower() for f in inv.get("mutating_functions", [])]
    for a, b in TWO_STEP_PAIRS:
        if any(a in fn for fn in funcs) and any(b in fn for fn in funcs):
            score += 5
            break
    # Asymmetric guards: some functions have modifiers, some don't
    fns_with_guards = inv.get("functions_with_guards", [])
    if fns_with_guards and len(fns_with_guards) < len(inv.get("mutating_functions", [])):
        score += 3
    return score


def _build_candidates(max_n: int) -> list[dict]:
    invariants = _load_json(INVARIANTS_FILE) or []
    if not isinstance(invariants, list):
        invariants = []

    # Include high-suspicion invariants of any category that have multi-tx potential
    high_sus = _load_json(HIGH_SUSPICION_FILE) or []
    if not isinstance(high_sus, list):
        high_sus = []
    all_inv = {i.get("invariant_id"): i for i in invariants}
    for i in high_sus:
        all_inv[i.get("invariant_id")] = i
    all_inv_list = list(all_inv.values())

    # Filter to STATE_MACHINE or any invariant with 2+ mutating functions that
    # match a two-step pair pattern
    candidates = []
    for inv in all_inv_list:
        if not inv.get("mutating_functions"):
            continue
        score = _score_invariant(inv)
        if score >= 3:
            inv["_multi_tx_score"] = score
            candidates.append(inv)

    candidates.sort(key=lambda i: -i.get("_multi_tx_score", 0))
    return candidates[:max_n]


def _call_claude(agent_spec: str, invariant: dict, source_excerpts: dict) -> dict:
    client = require_llm(skill="deep_analysis")
    user_msg = (
        "Analyse this STATE_MACHINE invariant for multi-transaction vulnerabilities.\n\n"
        f"Invariant:\n{json.dumps(invariant, indent=2)}\n\n"
        f"Relevant source excerpts:\n{json.dumps(source_excerpts, indent=2)}\n\n"
        "Work through STEP 1–5 from the agent spec. "
        "Return a JSON thread object with: thread_id, verdict, step_count, tx_sequence, "
        "min_blocks_between_steps, escalate, description, invariant_id, entry_conditions, "
        "violation_path, profit_or_damage."
    )
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=agent_spec,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = resp.content[0].text.strip()
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    if start != -1:
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
                        break
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Multi-transaction state machine vulnerability tracer"
    )
    parser.add_argument("--max-candidates", type=int, default=10,
                        help="Maximum number of invariants to trace (default 10)")
    args = parser.parse_args()

    agent_spec_path = AGENTS_DIR / "multi_tx_agent.md"
    if not agent_spec_path.exists():
        print(f"ERROR: {agent_spec_path} not found. Create agents/multi_tx_agent.md first.")
        return 1
    agent_spec = agent_spec_path.read_text()

    candidates = _build_candidates(args.max_candidates)
    if not candidates:
        print("No STATE_MACHINE invariants found. Run extract_invariants.py first.")
        return 0

    print(f"Multi-Transaction Trace — {len(candidates)} candidate invariant(s)")
    THREADS_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Read existing threads to avoid duplicate IDs
    existing_ids: set[str] = set()
    if THREADS_FILE.exists():
        for line in THREADS_FILE.read_text().splitlines():
            try:
                t = json.loads(line)
                existing_ids.add(t.get("thread_id", ""))
            except json.JSONDecodeError:
                continue

    # Assign MT-NNN IDs starting after the highest existing MT-NNN
    existing_mt = [int(tid[3:]) for tid in existing_ids if tid.startswith("MT-") and tid[3:].isdigit()]
    counter = max(existing_mt, default=0) + 1

    new_threads = []
    for inv in candidates:
        inv_id = inv.get("invariant_id", "unknown")
        funcs = inv.get("mutating_functions", [])
        excerpts = _load_source_for_functions(funcs)

        print(f"  Tracing {inv_id} (score={inv.get('_multi_tx_score', 0)}) …", end="", flush=True)
        try:
            result = _call_claude(agent_spec, inv, excerpts)
        except Exception as e:
            print(f" ERROR: {e}")
            continue

        if not result:
            print(" no result")
            continue

        verdict = result.get("verdict", "")
        if verdict == "DEAD_END":
            print(f" DEAD_END")
            continue

        thread_id = f"MT-{counter:03d}"
        counter += 1

        thread = {
            "thread_id": thread_id,
            "invariant_id": inv_id,
            "chain_id": result.get("chain_id", ""),
            "verdict": verdict,
            "escalate": result.get("escalate", verdict not in ("DEAD_END", "NEEDS_MORE_CONTEXT")),
            "description": result.get("description", ""),
            "entry_conditions": result.get("entry_conditions", ""),
            "violation_path": [
                tx.get("function", "")
                for tx in result.get("tx_sequence", [])
            ],
            "hop_traces": result.get("tx_sequence", []),
            "profit_or_damage": result.get("profit_or_damage", ""),
            "escalation_angles": result.get("escalation_angles", []),
            # MT-specific fields
            "step_count": result.get("step_count", 0),
            "min_blocks_between_steps": result.get("min_blocks_between_steps", 0),
            "multi_tx_pattern": result.get("multi_tx_pattern", ""),
        }

        with open(THREADS_FILE, "a") as f:
            f.write(json.dumps(thread, ensure_ascii=False) + "\n")
        new_threads.append(thread)
        print(f" => {thread_id} ({verdict})")

    escalatable = [t for t in new_threads if t.get("escalate")]
    print(f"\n  New MT threads written   : {len(new_threads)}")
    print(f"  Escalatable (non-dead-end): {len(escalatable)}")
    print(f"  Appended to: {THREADS_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
