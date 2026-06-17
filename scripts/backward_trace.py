#!/usr/bin/env python3
"""
backward_trace.py — Sink-to-source analysis (Stage 0c-bis).

Identifies high-value financial sinks, computes reverse reachability from
the call graph, pairs sinks with relevant invariants, and calls the
Backward Trace Agent to determine whether any path reaches a sink with
an invariant in a false state.

Appends to:
  data/threads/promising_threads.jsonl  — verdict != DEAD_END
  data/threads/dead_ends.jsonl          — fully traced, no violation

Usage:
    python scripts/backward_trace.py
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path
from llm_runtime import require_llm  # no-silent-fail: actionable message instead of credit spend/crash

ROOT             = Path(__file__).resolve().parent.parent
INTERACTIONS_DIR = audit_path("data/interactions")
INVARIANTS_DIR   = audit_path("data/invariants")
THREADS_DIR      = audit_path("data/threads")
STATIC_JSON      = audit_path("output") / "static.json"
AGENT_PROMPT     = ROOT / "agents" / "backward_trace_agent.md"

MODEL      = "claude-sonnet-4-6"
MAX_TOKENS = 4096
MAX_PAIRS  = 15

# Patterns that indicate a high-value financial sink
SINK_PATTERNS = [
    "transfer", "mint", "burn", "safeTransfer", "safeTransferFrom",
    "withdraw", "redeem", "liquidate", "repay", "borrow",
    "_balances", "totalSupply", "collateral", "debt",
]

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


def _is_sink(call_edge: dict) -> bool:
    """Identify whether a call edge targets a high-value sink."""
    callee = call_edge.get("callee", "").lower()
    state_written = " ".join(call_edge.get("state_written_after", [])).lower()
    for pattern in SINK_PATTERNS:
        if pattern.lower() in callee or pattern.lower() in state_written:
            return True
    return False


def _build_reverse_reachability(call_graph: list[dict]) -> dict[str, list[str]]:
    """
    Build a reverse call graph: sink_function -> [public entry points that can reach it].
    Returns a map from callee -> list of callers (direct + transitive public callers).
    """
    # Direct parent map: callee -> [direct callers]
    direct_parents: dict[str, list[str]] = defaultdict(list)
    all_nodes: set[str] = set()
    for edge in call_graph:
        caller = edge.get("caller", "")
        callee = edge.get("callee", "")
        if caller and callee:
            direct_parents[callee].append(caller)
            all_nodes.add(caller)
            all_nodes.add(callee)

    # For each node, walk up to find all public/external ancestors
    public_callsites = {n for n in all_nodes if _looks_public(n)}

    def ancestors(func: str, visited: set[str] | None = None) -> set[str]:
        if visited is None:
            visited = set()
        visited.add(func)
        result: set[str] = set()
        for parent in direct_parents.get(func, []):
            if parent in visited:
                continue
            if parent in public_callsites:
                result.add(parent)
            result |= ancestors(parent, visited)
        return result

    reachability: dict[str, list[str]] = {}
    for edge in call_graph:
        callee = edge.get("callee", "")
        if callee and _is_sink(edge) and callee not in reachability:
            reachable_from = ancestors(callee)
            if reachable_from:
                reachability[callee] = list(reachable_from)
    return reachability


def _looks_public(func_name: str) -> bool:
    """Heuristic: functions not prefixed with _ are likely public."""
    parts = func_name.split(".")
    name = parts[-1] if parts else func_name
    return not name.startswith("_") and not name.startswith("internal")


def _extract_source_for_path(path_funcs: list[str]) -> dict[str, str]:
    excerpts: dict[str, str] = {}
    func_names = {f.split(".")[-1] for f in path_funcs if f}

    candidates: list[Path] = []
    for cand in ["contracts", "src"]:
        p = ROOT / cand
        if p.is_dir():
            for ext in CONTRACT_EXTENSIONS:
                candidates.extend(p.rglob(f"*{ext}"))

    static = _load_json(STATIC_JSON)
    if isinstance(static, dict):
        cp = static.get("contract_path")
        if cp:
            p = ROOT / cp
            if p.is_file() and p.suffix in CONTRACT_EXTENSIONS:
                candidates.append(p)

    for p in candidates:
        try:
            source = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = source.splitlines()
        for fn in func_names:
            for i, line in enumerate(lines):
                if fn in line and ("fn " in line or "function " in line):
                    start = max(0, i - 2)
                    end = min(len(lines), i + 40)
                    key = f"{p.name}::{fn}"
                    excerpts[key] = "\n".join(lines[start:end])
    return excerpts


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


def _invariant_matches_sink(inv: dict, sink_func: str, sink_edge: dict) -> bool:
    """Check whether an invariant is relevant to a given sink."""
    sink_vars = set(sink_edge.get("state_written_after", []))
    sink_func_lower = sink_func.lower()
    inv_vars = set(inv.get("state_variables_involved", []))
    inv_funcs = set(f.lower() for f in inv.get("mutating_functions", []))
    # Match if invariant vars overlap with sink writes, or sink func is a mutator
    if inv_vars & sink_vars:
        return True
    if any(s in sink_func_lower for s in inv_funcs):
        return True
    return False


def main() -> int:
    THREADS_DIR.mkdir(parents=True, exist_ok=True)
    promising_path = THREADS_DIR / "promising_threads.jsonl"
    dead_ends_path = THREADS_DIR / "dead_ends.jsonl"

    print("Stage 0c-bis — Backward Trace Analysis (sink-to-source)")

    # Load call graph
    call_graph_data = _load_json(INTERACTIONS_DIR / "call_graph.json")
    if not isinstance(call_graph_data, dict):
        print("  No call graph found. Run map_interactions.py first.")
        return 0

    call_edges: list[dict] = call_graph_data.get("call_graph", [])
    if not call_edges:
        print("  Call graph is empty — nothing to trace.")
        return 0
    print(f"  Loaded {len(call_edges)} call edges")

    # Build reverse reachability for sinks
    print("  Identifying high-value sinks and computing reverse reachability …")
    reachability = _build_reverse_reachability(call_edges)
    if not reachability:
        print("  No reachable sinks found. Check that call graph has state_written_after fields.")
        return 0
    print(f"  Found {len(reachability)} unique sink function(s) with public entry points")

    # Load high-suspicion invariants
    invariants = _load_json(INVARIANTS_DIR / "high_suspicion.json")
    if not isinstance(invariants, list) or not invariants:
        print("  No high-suspicion invariants. Run extract_invariants.py first.")
        return 0
    print(f"  Loaded {len(invariants)} high-suspicion invariant(s)")

    # Build sink_edge lookup
    sink_edge_map: dict[str, dict] = {}
    for edge in call_edges:
        callee = edge.get("callee", "")
        if callee and _is_sink(edge):
            sink_edge_map[callee] = edge

    # Pair each sink with matching invariants
    pairs: list[tuple[str, list[str], dict, dict]] = []
    for sink_func, entry_points in reachability.items():
        sink_edge = sink_edge_map.get(sink_func, {})
        for inv in invariants:
            if _invariant_matches_sink(inv, sink_func, sink_edge):
                score = float(inv.get("suspicion_score", 1))
                pairs.append((sink_func, entry_points, inv, sink_edge))

    # Sort by invariant suspicion score descending, take top MAX_PAIRS
    pairs.sort(key=lambda p: float(p[2].get("suspicion_score", 0)), reverse=True)
    pairs = pairs[:MAX_PAIRS]
    print(f"  Paired: {len(pairs)} sink × invariant combination(s) (top {MAX_PAIRS})")

    if not pairs:
        print("  No overlapping sink-invariant pairs found.")
        return 0

    if not AGENT_PROMPT.exists():
        print(f"  Agent prompt not found: {AGENT_PROMPT}")
        return 1
    system_prompt = AGENT_PROMPT.read_text(encoding="utf-8")

    bt_counter = _count_existing_bt_threads(promising_path, dead_ends_path)
    verdict_counts: dict[str, int] = {}

    for idx, (sink_func, entry_points, inv, sink_edge) in enumerate(pairs, 1):
        bt_counter += 1
        thread_id = f"BT-{bt_counter:03d}"
        inv_id = inv.get("invariant_id", "?")
        print(f"\n  [{idx}/{len(pairs)}] {inv_id} → sink:{sink_func.split('.')[-1]} …", end="", flush=True)

        path_funcs = list(entry_points) + [sink_func]
        excerpts = _extract_source_for_path(path_funcs)

        user_payload = {
            "thread_id": thread_id,
            "sink": {
                "function": sink_func,
                "state_written": sink_edge.get("state_written_after", []),
                "significance": "high-value financial operation",
                "call_type": sink_edge.get("call_type", ""),
            },
            "entry_points": entry_points,
            "reachability_path": path_funcs,
            "invariant": inv,
            "source_excerpts": excerpts,
        }

        try:
            raw = _call_claude(system_prompt, json.dumps(user_payload, ensure_ascii=False))
        except Exception as e:
            print(f" ERROR: {e}")
            continue

        thread = _extract_json_object(raw)
        if not thread:
            print(" (no parseable JSON — skipping)")
            continue

        thread.setdefault("thread_id", thread_id)
        thread.setdefault("invariant_id", inv_id)
        thread.setdefault("chain_id", f"SINK-{sink_func.split('.')[-1]}")
        thread.setdefault("escalate", thread.get("verdict", "") not in ("DEAD_END", "NEEDS_MORE_CONTEXT"))

        verdict = thread.get("verdict", "UNKNOWN")
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        print(f" {verdict}")

        if verdict == "DEAD_END":
            _append_jsonl(dead_ends_path, thread)
        else:
            _append_jsonl(promising_path, thread)

    print(f"\n  Results:")
    for v, c in sorted(verdict_counts.items()):
        print(f"    {v}: {c}")
    print(f"\n  Appended to: {promising_path}")
    return 0


def _count_existing_bt_threads(promising: Path, dead: Path) -> int:
    """Count existing BT-* entries so we don't collide with DT-* IDs."""
    count = 0
    for path in [promising, dead]:
        for entry in _load_jsonl(path):
            tid = entry.get("thread_id", "")
            if tid.startswith("BT-"):
                try:
                    n = int(tid[3:])
                    count = max(count, n)
                except ValueError:
                    pass
    return count


if __name__ == "__main__":
    sys.exit(main())
