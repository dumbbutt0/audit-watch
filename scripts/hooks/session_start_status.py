#!/usr/bin/env python3
"""
session_start_status.py — WARN-ONLY SessionStart hook (read-only).

Surfaces the calibration + workflow state at the start of every Claude Code session so the
"add more agents before closing the feedback loop" mistake can't happen blind, and so the
human-review backlog is always visible. This hook NEVER blocks and NEVER writes trusted state.

Shows:
    • active audit (id / name) + recommended next action (from generate_status)
    • LLM pre-flight (ANTHROPIC_API_KEY present? credit-free skill fallbacks)
    • cross-audit calibration headline (FP / recall / PoC-success with n) from compute_metrics
    • active-audit ground-truth count, needs_human_review count, unpromoted learning candidates
    • last failed pre-submission gate (if any)

Writes (safe, non-trusted):
    audits/<id>/data/gates/session_start_status.json
    documentation/metrics/session_status_latest.md

Exit code is ALWAYS 0 (informational). Run manually:  python scripts/hooks/session_start_status.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _hooklib as h

_PROJECT_ROOT = h._SCRIPTS_DIR.parent


def _metrics_headline() -> dict:
    try:
        import compute_metrics
        m = compute_metrics.compute()
    except Exception as e:
        return {"error": f"compute_metrics unavailable: {e}"}

    def fmt(r):
        if not isinstance(r, dict):
            return "n/a"
        return f"{r['value']} (n={r['n']})" if r.get("value") is not None else r.get("state", "n/a")

    return {
        "audits_scanned": m.get("audits_scanned"),
        "ground_truth_records": m.get("ground_truth_records"),
        "false_positive_rate": fmt(m.get("false_positive_rate")),
        "recall_on_valid": fmt(m.get("recall_on_valid")),
        "poc_success_rate": fmt(m.get("poc_success_rate")),
    }


def _preflight() -> str:
    try:
        import llm_runtime
        # Show the full eval-critical path plus the post-pause stages, so the api-free
        # routing (which stage → which /skill) is visible at session start.
        return llm_runtime.preflight([
            "deep_analysis", "cross_agent_connector", "synthesize_compound",
            "multi_pass_confirm", "triage", "poc",
        ])
    except Exception as e:
        return f"LLM pre-flight unavailable: {e}"


def _pending_skill() -> str | None:
    """If the pipeline is parked at a skill-pending pause, name the next /skill to run."""
    def exists(*parts: str) -> bool:
        p = h.audit_file(*parts)
        return bool(p and p.exists())

    if exists("data", "invariants", "_bundles", "index.json") and \
       not exists("data", "invariants", "_deep_analysis_complete.json") and \
       not exists("data", "invariants", "protocol_invariants.json"):
        return "/deep-analysis  (then ./run_pipeline.sh analyze-resume)"
    if exists("data", "triage", "_bundles", "index.json") and \
       not exists("data", "triage", "_decisions.json"):
        return "/triage  (then python scripts/triage_write.py → ./run_pipeline.sh review-gate)"
    return None


def _next_action() -> dict:
    try:
        import generate_status
        st = generate_status.build_status()
        return {
            "current_layer_label": st.get("current_layer_label"),
            "next_action": st.get("next_action"),
            "next_command": st.get("next_command"),
            "submit_ready_count": st.get("submit_ready_count"),
        }
    except Exception as e:
        return {"error": f"generate_status unavailable: {e}"}


def _last_failed_gate() -> str | None:
    rows = h.load_jsonl(h.audit_file("data/triage", "gate_results.jsonl"))
    rejects = [r.get("finding_id") for r in rows if r.get("overall_verdict") == "REJECT"]
    return f"{len(rejects)} REJECT ({', '.join(filter(None, rejects))})" if rejects else None


def _proposed_count() -> int:
    pdir = h.audit_file("data/learning", "_proposed")
    if pdir is None or not pdir.exists():
        return 0
    total = 0
    for p in pdir.glob("*.jsonl"):
        total += sum(1 for ln in p.read_text().splitlines() if ln.strip())
    return total


def _outcomes_pending() -> int:
    """Real-world accepted findings with no recorded outcome (closing them measures FP/recall). Write-free."""
    try:
        import calibration_worklist as cw
        return cw.pending_count()
    except Exception:
        return 0


def build_state() -> dict:
    aid = h.active_audit_id()
    try:
        meta = h.ctx.get_audit_meta()
    except Exception:
        meta = {}
    gt = h.load_jsonl(h.audit_file("data/evaluation", "ground_truth.jsonl"))
    nhr = h.load_jsonl(h.audit_file("data/evaluation", "needs_human_review.jsonl"))
    return {
        "generated_at": h.now(),
        "active_audit": aid,
        "audit_name": meta.get("name", ""),
        "platform": meta.get("platform", ""),
        "deadline": meta.get("deadline", ""),
        "next_action": _next_action(),
        "pending_skill": _pending_skill(),
        "llm_preflight": _preflight(),
        "calibration": _metrics_headline(),
        "active_ground_truth_records": len(gt),
        "outcomes_pending": _outcomes_pending(),
        "needs_human_review_pending": len(nhr),
        "unpromoted_learning_candidates": _proposed_count(),
        "last_failed_gate": _last_failed_gate(),
    }


def render_md(s: dict) -> str:
    cal = s.get("calibration", {})
    na = s.get("next_action", {})
    lines = [
        "# Session Status (latest)",
        f"_Generated {s['generated_at']}_\n",
        f"**Active audit:** `{s.get('active_audit') or '(none)'}`"
        + (f" — {s['audit_name']}" if s.get("audit_name") else ""),
        f"**Next action:** {na.get('next_action', '?')}  "
        f"(`{na.get('next_command', '')}`)" if isinstance(na, dict) else "",
        "",
        "## Calibration (cross-audit)",
        f"- FP rate: {cal.get('false_positive_rate', 'n/a')}",
        f"- Recall on valid: {cal.get('recall_on_valid', 'n/a')}",
        f"- PoC success: {cal.get('poc_success_rate', 'n/a')}",
        f"- Ground-truth records (all audits): {cal.get('ground_truth_records', '?')} "
        f"across {cal.get('audits_scanned', '?')} audits",
        "",
        "## Backlog (this audit)",
        f"- Ground-truth records: {s.get('active_ground_truth_records')}",
        f"- Accepted findings awaiting an outcome: {s.get('outcomes_pending')} "
        f"(record via scripts/record_outcome.py to close calibration)",
        f"- needs_human_review pending: {s.get('needs_human_review_pending')}",
        f"- Unpromoted learning candidates: {s.get('unpromoted_learning_candidates')}",
        f"- Last failed gate: {s.get('last_failed_gate') or 'none'}",
        "",
        "## LLM pre-flight",
        "```",
        str(s.get("llm_preflight", "")),
        "```",
    ]
    return "\n".join(l for l in lines if l is not None) + "\n"


def render_console(s: dict) -> str:
    cal = s.get("calibration", {})
    na = s.get("next_action", {}) or {}
    parts = [
        "── Audit-Watch session status ──",
        f"  audit: {s.get('active_audit') or '(none)'}"
        + (f" ({s['audit_name']})" if s.get("audit_name") else ""),
    ]
    if isinstance(na, dict) and na.get("next_action"):
        parts.append(f"  next: {na.get('next_action')}  [{na.get('next_command', '')}]")
    if s.get("pending_skill"):
        parts.append(f"  ⏸ skill pending: {s['pending_skill']}")
    parts += [
        f"  calibration: FP={cal.get('false_positive_rate', 'n/a')}  "
        f"recall={cal.get('recall_on_valid', 'n/a')}  PoC={cal.get('poc_success_rate', 'n/a')}",
        f"  backlog: needs_human_review={s.get('needs_human_review_pending')}  "
        f"outcomes_pending={s.get('outcomes_pending')}  "
        f"unpromoted_learning={s.get('unpromoted_learning_candidates')}  "
        f"last_failed_gate={s.get('last_failed_gate') or 'none'}",
    ]
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description="SessionStart status surface (warn-only, read-only)")
    ap.add_argument("--dry-run", action="store_true", help="Print state; write nothing")
    ap.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    args = ap.parse_args()

    h.read_hook_input()  # drain stdin if invoked as a hook; payload unused for SessionStart

    try:
        state = build_state()
    except Exception as e:
        # Warn-only contract: never fail the session.
        print(f"[audit-watch hook] session status unavailable: {e}", file=sys.stderr)
        return h.ALLOW

    if not args.dry_run:
        h.write_gate_artifact(["session_start_status.json"], state)
        try:
            out_md = _PROJECT_ROOT / "documentation" / "metrics" / "session_status_latest.md"
            out_md.parent.mkdir(parents=True, exist_ok=True)
            out_md.write_text(render_md(state))
        except Exception:
            pass

    if args.json:
        print(json.dumps(state, indent=2))
    else:
        print(render_console(state))
    return h.ALLOW  # always allow


if __name__ == "__main__":
    sys.exit(main())
