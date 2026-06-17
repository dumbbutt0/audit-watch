#!/usr/bin/env python3
"""
block_api_scripts.py — PreToolUse(Bash) guard for api-free mode.

When config/runtime_policy.json pins api_free, the pipeline must never reach the Anthropic API.
Most stages already route to a /skill, but an operator (or the model) could still invoke a
deprecated API-only script directly (e.g. `python scripts/extract_invariants.py …`), which would
either SystemExit with a terse message or — if a stray key is present and api_free were bypassed —
spend credits. This hook intercepts those direct calls and points to the credit-free route instead.

Contract: reads PreToolUse JSON from stdin; exit 2 blocks the Bash call (stderr shown to the model);
exit 0 allows. Only blocks when api_free is active and the command names a deprecated script.
Bypass with AUDITWATCH_HOOK_OVERRIDE=1. Does NOT block the new triplet (deep_analysis_prepare/
deep_analysis_write, triage_prepare/triage_write) or run_pipeline.sh orchestration.

Manually runnable:  echo '{"tool_input":{"command":"python scripts/extract_invariants.py"}}' | python scripts/hooks/block_api_scripts.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _hooklib as hooklib  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from llm_runtime import api_free_mode
except Exception:  # pragma: no cover - llm_runtime should always import
    def api_free_mode() -> bool:
        return False

# Deprecated API-only script basename → the credit-free route to use instead.
DEPRECATED = {
    # Step 0 deep analysis → /deep-analysis triplet
    "run_deep_analysis.py":      "/deep-analysis skill (./run_pipeline.sh analyze pauses for it, then analyze-resume)",
    "extract_invariants.py":     "/deep-analysis skill (writes data/invariants/protocol_invariants.json in-session)",
    "map_interactions.py":       "/deep-analysis skill (writes data/interactions/call_graph.json in-session)",
    "deep_trace.py":             "/deep-analysis skill (writes data/threads/*.jsonl in-session)",
    "backward_trace.py":         "/deep-analysis skill (writes data/threads/*.jsonl in-session)",
    "escalate_threads.py":       "/deep-analysis skill (writes output/findings_deep_trace.json in-session)",
    "multi_tx_trace.py":         "/deep-analysis skill (appends MT- threads in-session)",
    "generate_fuzzing_harness.py": "/deep-analysis skill (writes the Echidna harness in-session)",
    "smt_check_invariants.py":   "/deep-analysis skill (writes the Z3 encoding in-session)",
    # Step 4 triage → /triage triplet
    "triage_findings.py":        "/triage skill, then `python scripts/triage_write.py`",
    # Step 5 reasoning + PoC + learning → not yet converted (P1/P2); off the review_gate path.
    "calibrate_severity.py":     "deferred (P1) — Step-5 severity reasoning is not yet API-free",
    "estimate_duplicate_risk.py":"deferred (P1) — Step-5 dup-risk reasoning is not yet API-free",
    "model_exploitability.py":   "deferred (P1) — Step-5 exploitability reasoning is not yet API-free",
    "judge_simulate.py":         "deferred (P1) — Step-5 judge simulation is not yet API-free",
    "reference_diff.py":         "deferred (P1) — reference-diff reasoning is not yet API-free",
    "generate_poc_plan.py":      "deferred (P2) — PoC generation is not yet API-free",
    "generate_poc_test.py":      "deferred (P2) — PoC generation is not yet API-free",
    "run_integrated_poc.py":     "deferred (P2) — PoC generation is not yet API-free",
    "record_fp_autopsy.py":      "deferred (P2) — FP autopsy is not yet API-free",
    "bulk_fp_autopsy.py":        "deferred (P2) — FP autopsy is not yet API-free",
}


def _invokes_script(cmd: str, script: str) -> bool:
    """True only if the command actually INVOKES <script> — i.e. it appears as the executed
    program after an interpreter (python/python3/sh/bash) or as a direct `./path` exec.

    This deliberately ignores mere mentions in `grep`/`cat`/`echo`/comments so read-only
    inspection of these scripts is never blocked. Pattern: an interpreter or `./` immediately
    precedes an optional path then the script basename at a token boundary.
    """
    esc = re.escape(script)
    pattern = rf"(?:(?:^|[;&|]|\b(?:python3?|sh|bash))\s+|\./)(?:[^\s;|&]*/)?{esc}(?:\s|$)"
    return re.search(pattern, cmd) is not None


def main() -> int:
    payload = hooklib.read_hook_input()
    cmd = hooklib.tool_command(payload)
    if not cmd:
        # Interactive / no command → nothing to guard.
        return hooklib.ALLOW
    if not api_free_mode():
        return hooklib.ALLOW  # API path explicitly enabled; don't interfere.
    if hooklib.override_active():
        return hooklib.emit_warn("api-free guard bypassed via AUDITWATCH_HOOK_OVERRIDE.")

    for script, route in DEPRECATED.items():
        if _invokes_script(cmd, script):
            return hooklib.emit_block(
                f"`{script}` is an API-backed stage, but api-free mode is pinned "
                f"(config/runtime_policy.json). Use the credit-free route instead: {route}."
            )
    return hooklib.ALLOW


if __name__ == "__main__":
    sys.exit(main())
