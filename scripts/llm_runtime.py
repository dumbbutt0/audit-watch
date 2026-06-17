#!/usr/bin/env python3
"""
llm_runtime.py — Single entry point for API-backed scripts to acquire a Claude client,
with a graceful, actionable failure when no key is present (instead of a cryptic SDK
TypeError mid-run).

Every API script should replace its bare `anthropic.Anthropic()` with:

    from llm_runtime import require_llm
    client = require_llm(skill="triage", bundle_hint="data/triage/_bundles/")

If ANTHROPIC_API_KEY is set, this returns a normal client (unchanged behavior). If not, it
raises SystemExit with a message naming the skill-in-session equivalent and the bundle path —
so the operator knows exactly how to proceed without an API key (the credit-free path).

Also exposes:
    llm_available() -> bool          # cheap key check, no client construction
    preflight(steps) -> str          # human-readable API/skill map for run_pipeline.sh
"""
from __future__ import annotations

import os
from pathlib import Path

# Map each API script/stage to its skill-in-session equivalent + bundle location.
# Used by the no-key error and by run_pipeline.sh preflight. "skill: null" means
# not yet converted (the recipe in api_dependency_audit.md applies).
SKILL_MAP: dict[str, dict] = {
    "triage":                  {"skill": "/triage",   "bundle": "data/triage/_bundles/", "optional": False},
    # Default `run_pipeline.sh full` enhancers — OPTIONAL: skip cleanly with no key so the
    # deterministic path (report_generator.py merge → gates → /triage) still completes.
    "multi_pass_confirm":      {"skill": None,        "bundle": "output/findings_confirmed.json", "optional": True},
    "synthesize_compound":     {"skill": None,        "bundle": "output/findings_*.json", "optional": True},
    "cross_agent_connector":   {"skill": None,        "bundle": "output/findings_*.json", "optional": True},
    # Step 5 / post-pause reasoning stages — REQUIRED: stop with actionable guidance (never silent).
    "calibrate_severity":      {"skill": None,        "bundle": "data/severity/", "optional": False},
    "estimate_duplicate_risk": {"skill": None,        "bundle": "data/duplicates/", "optional": False},
    "model_exploitability":    {"skill": None,        "bundle": "data/exploitability/", "optional": False},
    "judge_simulate":          {"skill": None,        "bundle": "data/judge_simulation/", "optional": False},
    "reference_diff":          {"skill": None,        "bundle": "data/reference_diff/", "optional": False},
    # Step 0 deep-analysis substages: extract_invariants, map_interactions, deep_trace, backward_trace,
    # multi_tx_trace, escalate_threads, generate_fuzzing_harness, smt_check. Converted to the
    # /deep-analysis skill-in-session triplet (deep_analysis_prepare.py → /deep-analysis → deep_analysis_write.py).
    "deep_analysis":           {"skill": "/deep-analysis", "bundle": "data/invariants/_bundles/", "optional": True},
    # Cheap coverage sweep over the manifest long tail — credit-free /coverage-sweep skill triplet
    # (coverage_sweep_prepare.py -> /coverage-sweep -> coverage_sweep_write.py). Optional enhancer.
    "coverage_sweep":          {"skill": "/coverage-sweep", "bundle": "output/coverage_sweep/_bundles/", "optional": True},
    # PoC validation semantic notes — credit-free /poc-validation skill triplet
    # (poc_validation_prepare.py -> /poc-validation -> poc_validation_write.py -> validate_poc.py).
    # Optional enhancer: with no notes the validator stays conservative (never auto-proven).
    "poc_validation":          {"skill": "/poc-validation", "bundle": "output/poc_validation/bundles/", "optional": True},
    # Phase-14 / Experiment E1 agentic deep-pass over detector candidates — credit-free /deep-pass triplet
    # (deep_pass_prepare.py -> /deep-pass -> deep_pass_write.py --eval). RESEARCH-ONLY: optional ⇒ never
    # hard-blocks a gate; the eval path writes deep_pass_audit.json and does NOT mutate dispositions.
    "deep_pass":               {"skill": "/deep-pass", "bundle": "output/deep_pass/_bundles/", "optional": True},
    # PoC generation (post-pause): generate_poc_plan, generate_poc_test, run_integrated_poc.
    "poc":                     {"skill": None,        "bundle": "pocs/", "optional": False},
    # FP-learning autopsies: record_fp_autopsy, bulk_fp_autopsy.
    "fp_autopsy":              {"skill": None,        "bundle": "data/fp_autopsies/", "optional": False},
    # KB embeddings (offline-cacheable) — optional enrichment.
    "solodit_scraper":         {"skill": None,        "bundle": "kb/chroma/", "optional": True},
}


_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_env() -> None:
    env = Path(".env")
    if not env.exists():
        env = _PROJECT_ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("\"'"))


def api_free_mode() -> bool:
    """True if the operator has pinned the pipeline to the credit-free (skill-in-session) path.

    Reads config/runtime_policy.json → "api_free". When true, llm_available() returns False
    even if ANTHROPIC_API_KEY is present, so every stage routes to its /skill instead of the
    Anthropic API. Env var AUDIT_WATCH_API_FREE=0 can override the config to re-enable the API.
    """
    override = os.environ.get("AUDIT_WATCH_API_FREE")
    if override is not None:
        return override.strip() not in ("0", "false", "False", "")
    policy = _PROJECT_ROOT / "config" / "runtime_policy.json"
    if not policy.exists():
        return False
    try:
        import json
        return bool(json.loads(policy.read_text()).get("api_free", False))
    except Exception:
        return False


def llm_available() -> bool:
    """True if an Anthropic API key is configured AND api_free mode is not pinned.

    In api_free mode (config/runtime_policy.json), this always returns False so the whole
    pipeline takes the in-session skill route — no direct Anthropic API calls, no credit spend.
    """
    if api_free_mode():
        return False
    _load_env()
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def require_llm(skill: str = "", bundle_hint: str = ""):
    """Return a configured anthropic.Anthropic client, or exit with an actionable message.

    `skill` keys into SKILL_MAP for the credit-free alternative; `bundle_hint` overrides
    the printed bundle path.
    """
    _load_env()
    if api_free_mode() or not os.environ.get("ANTHROPIC_API_KEY"):
        info = SKILL_MAP.get(skill, {})
        alt = info.get("skill")
        bundle = bundle_hint or info.get("bundle", "(see api_dependency_audit.md)")
        if alt:
            msg = (f"No ANTHROPIC_API_KEY set. Use the credit-free skill instead:\n"
                   f"    run the {alt} skill in Claude Code (bundle in {bundle}).")
        else:
            msg = (f"No ANTHROPIC_API_KEY set. This step ('{skill or 'unknown'}') is not yet "
                   f"converted to a skill.\n    Options: (a) export ANTHROPIC_API_KEY, or "
                   f"(b) follow the conversion recipe in "
                   f"documentation/refinement/api_dependency_audit.md.")
        raise SystemExit(f"[llm_runtime] {msg}")
    try:
        import anthropic
    except ImportError:
        raise SystemExit("[llm_runtime] anthropic SDK not installed: pip install anthropic")
    return anthropic.Anthropic()


def optional_llm(skill: str = ""):
    """Like require_llm(), but for OPTIONAL enhancer stages on the default pipeline path.

    Returns a configured client if a key is present; if not, prints a single
    skip-and-continue notice to stderr and returns None — so the caller can `if client is
    None: <skip cleanly>` and let the deterministic artifacts carry the run. Never raises,
    never burns credits, never silently disappears.
    """
    import sys
    _load_env()
    if api_free_mode() or not os.environ.get("ANTHROPIC_API_KEY"):
        info = SKILL_MAP.get(skill, {})
        alt = info.get("skill")
        tail = f" (credit-free alt: {alt})" if alt else " (deterministic artifacts carry the run)"
        print(f"[llm_runtime] No ANTHROPIC_API_KEY — skipping optional stage '{skill or 'unknown'}'"
              f"{tail}.", file=sys.stderr)
        return None
    try:
        import anthropic
    except ImportError:
        print("[llm_runtime] anthropic SDK not installed — skipping optional stage "
              f"'{skill or 'unknown'}'.", file=sys.stderr)
        return None
    return anthropic.Anthropic()


def preflight(steps: list[str]) -> str:
    """Return a human-readable API/skill map for the given upcoming step keys."""
    have = llm_available()
    if api_free_mode():
        header = "LLM pre-flight — API-FREE MODE pinned (config/runtime_policy.json): all stages route to in-session skills"
    else:
        header = f"LLM pre-flight — ANTHROPIC_API_KEY: {'present' if have else 'ABSENT'}"
    lines = [header]
    for s in steps:
        info = SKILL_MAP.get(s, {})
        alt = info.get("skill")
        if have:
            lines.append(f"  • {s}: API ready")
        elif alt:
            lines.append(f"  • {s}: no key → use {alt} (credit-free)")
        elif info.get("optional"):
            lines.append(f"  • {s}: no key → SKIP (optional; deterministic artifacts carry the run)")
        else:
            lines.append(f"  • {s}: no key → no skill yet; stops with an actionable message")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if "--have-key" in args:
        # Exit 0 if a key is configured, 1 if not — for run_pipeline.sh zero-API detection.
        sys.exit(0 if llm_available() else 1)
    print(preflight(args or list(SKILL_MAP.keys())))
