#!/usr/bin/env python3
"""
deep_analysis_write.py — Deterministic validator/finalizer for the /deep-analysis skill flow.

After the /deep-analysis skill has written the canonical Step-0 artifacts in-session, this script
validates they exist, parse, and carry the expected shape — then emits a completion marker the
pipeline reads. It never calls an API. It mirrors triage_write.py's "validate, never silent" posture:
core artifacts missing/malformed → non-zero exit with a clear message; optional artifacts → warning.

Usage:
    python scripts/deep_analysis_write.py
    python scripts/deep_analysis_write.py --allow-empty   # accept empty (no invariants/threads found)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402


def _load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return {"__parse_error__": str(e)}


def _count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text().splitlines() if line.strip())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-empty", action="store_true",
                    help="Accept a run where the skill legitimately found no invariants/threads.")
    args = ap.parse_args()

    inv_dir = audit_path("data/invariants")
    inter_dir = audit_path("data/interactions")
    threads_dir = audit_path("data/threads")
    out_dir = audit_path("output")

    errors: list[str] = []
    warnings: list[str] = []
    summary: dict = {}

    # 0a — invariants (core)
    invs = _load_json(inv_dir / "protocol_invariants.json")
    if invs is None:
        errors.append("data/invariants/protocol_invariants.json missing — run the /deep-analysis skill first")
    elif isinstance(invs, dict) and invs.get("__parse_error__"):
        errors.append(f"protocol_invariants.json invalid JSON: {invs['__parse_error__']}")
    elif not isinstance(invs, list):
        errors.append("protocol_invariants.json must be a JSON array of invariants")
    else:
        summary["invariants"] = len(invs)
        summary["high_suspicion"] = len(_load_json(inv_dir / "high_suspicion.json") or [])
        summary["medium_suspicion"] = len(_load_json(inv_dir / "medium_suspicion.json") or [])
        if not invs and not args.allow_empty:
            warnings.append("0 invariants extracted — unexpected for a non-trivial protocol "
                            "(re-run /deep-analysis, or pass --allow-empty if truly none)")

    # 0b — interactions (core)
    cg = _load_json(inter_dir / "call_graph.json")
    if cg is None:
        errors.append("data/interactions/call_graph.json missing — run the /deep-analysis skill first")
    elif isinstance(cg, dict) and cg.get("__parse_error__"):
        errors.append(f"call_graph.json invalid JSON: {cg['__parse_error__']}")
    elif not isinstance(cg, dict) or "interaction_chains" not in cg:
        errors.append("call_graph.json must be an object with keys call_graph/interaction_chains/trust_boundary_crossings")
    else:
        summary["interaction_chains"] = len(cg.get("interaction_chains", []))
        summary["call_graph_edges"] = len(cg.get("call_graph", []))
        summary["dangerous_chains"] = len(_load_json(inter_dir / "dangerous_chains.json") or [])

    # 0c/0c-bis/0f — threads (core)
    summary["promising_threads"] = _count_jsonl(threads_dir / "promising_threads.jsonl")
    summary["dead_ends"] = _count_jsonl(threads_dir / "dead_ends.jsonl")
    if not (threads_dir / "promising_threads.jsonl").exists() and \
       not (threads_dir / "dead_ends.jsonl").exists():
        errors.append("data/threads/*.jsonl missing — the deep_trace substage did not run")

    # 0d — escalated findings (core)
    dt = _load_json(out_dir / "findings_deep_trace.json")
    if dt is None:
        errors.append("output/findings_deep_trace.json missing — the escalate_threads substage did not run")
    elif isinstance(dt, dict) and dt.get("__parse_error__"):
        errors.append(f"findings_deep_trace.json invalid JSON: {dt['__parse_error__']}")
    elif not isinstance(dt, dict) or "findings" not in dt:
        errors.append("findings_deep_trace.json must be an object with a 'findings' array")
    else:
        summary["deep_trace_findings"] = len(dt.get("findings", []))

    if errors:
        print("[deep_analysis_write] VALIDATION FAILED — nothing finalized:")
        for e in errors:
            print(f"  ✗ {e}")
        print("\n  Fix: run `python scripts/deep_analysis_prepare.py --contract <path>` then the "
              "/deep-analysis skill, which writes these artifacts in-session.")
        return 1

    marker = inv_dir / "_deep_analysis_complete.json"
    marker.write_text(json.dumps({
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "path": "skill-in-session (/deep-analysis), no API",
        "summary": summary,
        "warnings": warnings,
    }, indent=2))

    print("[ok] deep-analysis validated (skill-in-session path, no API):")
    for k, v in summary.items():
        print(f"     {k}: {v}")
    for w in warnings:
        print(f"     [warn] {w}")
    print(f"     marker: {marker}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
