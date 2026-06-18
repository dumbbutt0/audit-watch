#!/usr/bin/env python3
"""
deep_analysis_prepare.py — Deterministic pre-processor for the /deep-analysis skill-in-session flow.

Replaces the API-backed Step 0 deep invariant analysis (run_deep_analysis.py and its 8 substages:
extract_invariants, map_interactions, deep_trace, backward_trace, escalate_threads, multi_tx_trace,
generate_fuzzing_harness, smt_check_invariants) with a credit-free triplet:

    deep_analysis_prepare.py  → /deep-analysis skill (in-session) → deep_analysis_write.py

This prepare step builds a lightweight bundle so the skill knows exactly what to read, which prompts
to apply, and which canonical artifacts to produce. It embeds NO full source (the skill reads source
files directly via the Read tool, like the Step-2 specialist agents) — only the scope list, a
static-analysis summary, prompt pointers, the substage plan, and the output targets.

Usage:
    python scripts/deep_analysis_prepare.py --contract <path_or_dir> [--mode deep]
                                            [--skip-fuzzing] [--skip-smt] [--skip-multi-tx] [--skip-backward]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"
CONTRACT_EXTENSIONS = {".sol", ".rs", ".vy", ".move"}

# The substage plan the /deep-analysis skill executes in order. Each entry names the reasoning
# prompt to apply and the canonical artifact(s) to write — identical schemas to the API scripts.
SUBSTAGE_PLAN = [
    {"stage": "0a-extract_invariants", "prompt": "invariant_extractor.md",
     "outputs": ["data/invariants/protocol_invariants.json",
                 "data/invariants/high_suspicion.json",
                 "data/invariants/medium_suspicion.json"]},
    {"stage": "0b-map_interactions", "prompt": "interaction_mapper.md",
     "outputs": ["data/interactions/call_graph.json",
                 "data/interactions/dangerous_chains.json"]},
    {"stage": "0c-deep_trace", "prompt": "deep_trace.md",
     "outputs": ["data/threads/promising_threads.jsonl",
                 "data/threads/dead_ends.jsonl"]},
    {"stage": "0c-bis-backward_trace", "prompt": "deep_trace.md",
     "outputs": ["data/threads/promising_threads.jsonl",
                 "data/threads/dead_ends.jsonl"], "skip_flag": "skip_backward"},
    {"stage": "0f-multi_tx_trace", "prompt": "deep_trace.md",
     "outputs": ["data/threads/promising_threads.jsonl"], "skip_flag": "skip_multi_tx"},
    {"stage": "0d-escalate_threads", "prompt": "impact_chain_escalation.md",
     "outputs": ["output/findings_deep_trace.json"]},
]


def _scope_files(contract: Path) -> list[dict]:
    """List contract source files in scope with line counts (lightweight; no content embedded)."""
    files: list[dict] = []
    paths = [contract] if contract.is_file() else sorted(contract.rglob("*"))
    for p in paths:
        if p.is_file() and p.suffix in CONTRACT_EXTENSIONS:
            try:
                n = sum(1 for _ in p.open("r", encoding="utf-8", errors="replace"))
            except OSError:
                n = 0
            files.append({"path": str(p), "lines": n})
    return files


def _static_summary() -> dict:
    static_path = audit_path("output") / "static.json"
    if not static_path.exists():
        return {"present": False}
    try:
        s = json.loads(static_path.read_text())
    except (json.JSONDecodeError, OSError):
        return {"present": True, "parse_error": True}
    # Surface the flags downstream substages care about, without dumping the whole file.
    summary = {"present": True}
    for k in ("is_erc4626", "is_proxy", "has_transient_storage", "is_upgradeable"):
        if k in s:
            summary[k] = s[k]
    for k in ("detectors", "findings", "external_calls", "state_variables"):
        v = s.get(k)
        if isinstance(v, list):
            summary[f"{k}_count"] = len(v)
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepare the /deep-analysis skill bundle (no API).")
    ap.add_argument("--contract", required=True, help="Path to contract file or directory")
    ap.add_argument("--mode", choices=["normal", "deep"], default="normal")
    ap.add_argument("--skip-backward", action="store_true")
    ap.add_argument("--skip-fuzzing", action="store_true")
    ap.add_argument("--skip-smt", action="store_true")
    ap.add_argument("--skip-multi-tx", action="store_true")
    args = ap.parse_args()

    contract = Path(args.contract)
    if not contract.exists():
        # Tolerate paths relative to project root.
        contract = ROOT / args.contract
    if not contract.exists():
        raise SystemExit(f"[deep_analysis_prepare] contract path not found: {args.contract}")

    bundle_dir = audit_path("data/invariants") / "_bundles"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    skips = {
        "skip_backward": args.skip_backward,
        "skip_multi_tx": args.skip_multi_tx,
        "skip_fuzzing": args.skip_fuzzing,
        "skip_smt": args.skip_smt,
    }
    plan = [s for s in SUBSTAGE_PLAN if not skips.get(s.get("skip_flag", ""), False)]

    scope = _scope_files(contract)
    bundle = {
        "contract_path": str(contract),
        "mode": args.mode,
        "skips": skips,
        "optional_tool_stages": {
            "generate_fuzzing_harness": (not args.skip_fuzzing),  # writes Echidna harness; runner is deterministic
            "smt_check_invariants": (not args.skip_smt),          # writes Z3 encoding; runner is deterministic
        },
        "scope_files": scope,
        "scope_file_count": len(scope),
        "static_summary": _static_summary(),
        "prompt_dir": str(PROMPTS),
        "substage_plan": plan,
        "instructions": (
            "Read each prompt under prompt_dir and apply it in-session, reading the listed scope "
            "files via the Read tool (do NOT call any API script). Write each substage's outputs to "
            "the exact paths in substage_plan using the documented schema. Then run "
            "python scripts/deep_analysis_write.py to validate."
        ),
    }

    (bundle_dir / "index.json").write_text(json.dumps(bundle, indent=2, ensure_ascii=False))

    print(f"[ok] deep-analysis bundle ready → {bundle_dir / 'index.json'}")
    print(f"     scope: {len(scope)} source files · mode={args.mode} · substages={len(plan)}")
    print("     Next: run the /deep-analysis skill in Claude Code, then")
    print("           python scripts/deep_analysis_write.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
