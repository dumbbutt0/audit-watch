#!/usr/bin/env python3
"""
run_deep_analysis.py — Convenience orchestrator for the deep invariant analysis pipeline.

Stages:
  Stage 0a: extract_invariants.py
  Stage 0b: map_interactions.py
  Stage 0c: deep_trace.py (forward + CROSS_CONTRACT second pass)
  Stage 0c-bis: backward_trace.py (sink-to-source)
  Stage 0d: escalate_threads.py
  Stage 0d-fuzz: generate_fuzzing_harness.py (Echidna properties)
  Stage 0e: smt_check_invariants.py (Z3 arithmetic falsification)
  Stage 0f: multi_tx_trace.py (multi-transaction state machine)

Usage:
    python scripts/run_deep_analysis.py --contract <path_or_dir>
    python scripts/run_deep_analysis.py --contract <path_or_dir> --mode deep
    python scripts/run_deep_analysis.py --contract <path_or_dir> --skip-fuzzing --skip-smt
    python scripts/run_deep_analysis.py --contract <path_or_dir> --skip-multi-tx
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def _run_stage(label: str, cmd: list[str]) -> int:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    try:
        sys.path.insert(0, str(ROOT))
        from viz.event_emitter import emit as _viz_emit
        _viz_emit("AGENT_SPAWNED", source_agent="run_deep_analysis", payload={
            "spawned_agent": label,
            "command": cmd[1] if len(cmd) > 1 else "",
        })
    except Exception:
        pass
    t0 = time.monotonic()
    result = subprocess.run(cmd, cwd=ROOT)
    elapsed = time.monotonic() - t0
    status = "OK" if result.returncode == 0 else f"FAILED (exit {result.returncode})"
    print(f"\n  ─── {label}: {status} in {elapsed:.1f}s ───")
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the full deep invariant analysis pipeline"
    )
    parser.add_argument("--contract", required=True, help="Path to contract file or directory")
    parser.add_argument("--mode", choices=["normal", "deep"], default="normal",
                        help="Analysis depth (deep traces 50 pairs instead of 20)")
    parser.add_argument("--skip-backward", action="store_true",
                        help="Skip backward (sink-to-source) trace")
    parser.add_argument("--skip-fuzzing", action="store_true",
                        help="Skip Echidna harness generation")
    parser.add_argument("--skip-smt", action="store_true",
                        help="Skip Z3 SMT arithmetic checking")
    parser.add_argument("--skip-multi-tx", action="store_true",
                        help="Skip multi-transaction state machine trace")
    args = parser.parse_args()

    contract = args.contract
    python = sys.executable

    # In deep mode, trace up to 50 pairs and include score-3 soft-flag pass
    deep_trace_cmd = [python, str(SCRIPTS / "deep_trace.py")]
    if args.mode == "deep":
        deep_trace_cmd += ["--max-pairs", "50", "--include-medium"]

    print("\nDeep Invariant Analysis Pipeline")
    print(f"Contract: {contract}  mode: {args.mode}")
    total_start = time.monotonic()

    # ── Hermes routing consult ────────────────────────────────────────────────
    try:
        from scripts.hermes_bridge import get_routing_recommendation, get_agent_priority
        from audit_context import get_audit_meta as _get_meta
        _da_meta = _get_meta()
        _da_audit_id = _da_meta.get("audit_id", "")
        _da_deadline = _da_meta.get("deadline", "")
        _da_days: int | None = None
        if _da_deadline and _da_deadline != "open":
            from datetime import datetime, timezone
            try:
                _dl = datetime.fromisoformat(_da_deadline.replace("Z", "+00:00"))
                _da_days = (_dl - datetime.now(timezone.utc)).days
            except ValueError:
                pass
        _da_rec = get_routing_recommendation("pre_deep_analysis", {
            "audit_id": _da_audit_id,
            "deadline_days": _da_days,
            "submit_count": 0,
            "protocol_type": _da_meta.get("contest", ""),
        })
        if _da_rec["confidence"] > 0.5:
            print(f"\n[HERMES] Routing: {_da_rec['recommendation']}")
            if _da_rec.get("priority_agents"):
                print(f"[HERMES] Priority agents: {', '.join(_da_rec['priority_agents'])}")
            if _da_rec.get("escalate_to_human"):
                print(f"[HERMES] ⚠ Human escalation: {_da_rec['escalation_reason']}")
    except Exception:
        pass

    stages = [
        ("Stage 0a — Invariant Extraction",
         [python, str(SCRIPTS / "extract_invariants.py"), "--contract", contract],
         False),
        ("Stage 0b — Interaction Mapping",
         [python, str(SCRIPTS / "map_interactions.py"), "--contract", contract],
         False),
        ("Stage 0c — Deep Trace (forward)",
         deep_trace_cmd,
         False),
        ("Stage 0c-bis — Backward Trace (sink-to-source)",
         [python, str(SCRIPTS / "backward_trace.py")],
         args.skip_backward),
        ("Stage 0d — Thread Escalation",
         [python, str(SCRIPTS / "escalate_threads.py")],
         False),
        ("Stage 0d-brief — Step 0 Human-Readable Brief",
         [python, str(SCRIPTS / "generate_step0_brief.py")],
         False),
        ("Stage 0d-fuzz — Fuzzing Harness Generation",
         [python, str(SCRIPTS / "generate_fuzzing_harness.py"), "--contract", contract],
         args.skip_fuzzing),
        ("Stage 0e — SMT Arithmetic Checking",
         [python, str(SCRIPTS / "smt_check_invariants.py")],
         args.skip_smt),
        ("Stage 0f — Multi-Transaction State Machine Trace",
         [python, str(SCRIPTS / "multi_tx_trace.py")],
         args.skip_multi_tx),
    ]

    failed = []
    skipped = []
    for label, cmd, skip in stages:
        if skip:
            print(f"\n  [SKIP] {label}")
            skipped.append(label)
            continue
        rc = _run_stage(label, cmd)
        if rc != 0:
            failed.append(label)
            # Continue running subsequent stages — outputs may be partial

    total_elapsed = time.monotonic() - total_start
    print(f"\n{'='*60}")
    print(f"  Deep Analysis Complete — {total_elapsed:.1f}s total")
    if skipped:
        print(f"  Skipped: {', '.join(skipped)}")
    if failed:
        print(f"  WARNING: {len(failed)} stage(s) failed: {', '.join(failed)}")
    else:
        print("  All active stages completed successfully.")
    print(f"{'='*60}")
    print()
    print("Outputs:")
    print("  data/invariants/protocol_invariants.json   all protocol invariants")
    print("  data/invariants/high_suspicion.json        suspicion_score >= 4")
    print("  data/interactions/call_graph.json          full interaction map")
    print("  data/interactions/dangerous_chains.json    danger_score >= 4")
    print("  data/invariants/medium_suspicion.json      score-3 invariants (soft-flag watch list)")
    print("  data/threads/promising_threads.jsonl       threads to escalate (forward + backward)")
    print("  data/threads/dead_ends.jsonl               fully traced, no violation")
    print("  data/threads/fuzzing_threads.jsonl         Echidna-falsified properties (if run)")
    print("  data/threads/promising_threads.jsonl       MT-* threads appended by multi_tx_trace")
    print("  output/findings_deep_trace.json            escalated findings")
    print("  output/findings_smt.json                   SMT-falsified arithmetic invariants")
    print("  output/step0_brief.md                      ← READ THIS before Step 1")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
