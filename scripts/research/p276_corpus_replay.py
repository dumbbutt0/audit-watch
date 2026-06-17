#!/usr/bin/env python3
"""P276 — SUPERVISED_EVAL corpus replay driver (Pass A, NO answer key).

RESEARCH-ONLY / ADVISORY / UN-WIRED. Drives the FROZEN research funnel per eval contest from its existing
coverage_manifest.json, with NO answer-key access:

  coverage_manifest (existing) -> regen checkpoints -> P264 recall harness (shadow)
    -> auto-build P273 coverage input (class signals = locus name tokens)  -> P273 router
    -> auto-build P269 triage input (heuristic impact dims by routed class) -> P269 triage

The frozen modules are invoked as black boxes (byte-identical); this driver only builds their *inputs* from the
harness's own advisory candidates (source-derived locus tokens), never editing them. Emits a per-contest replay
bundle. No severity / reportable / submission / confirmed — pure advisory.

Usage:
  python scripts/research/p276_corpus_replay.py --audit-id <eval-audit-id> --out-dir <dir> [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
RESEARCH = SCRIPTS / "research"
CFG_COVERAGE = ROOT / "config/research_award_class_coverage_router.json"

LABEL = "SUPERVISED_EVAL"

# Heuristic impact_class per routed award class (deterministic; documented in LIMITATIONS as coarse).
_CLASS_TO_IMPACT = {
    "ACCOUNTING_LIQUIDATION_BAD_DEBT": "cross_domain_accounting_mismatch",
    "ACCESS_CONTROL_AUTHORIZATION": "cross_domain_accounting_mismatch",
    "ORDER_VALIDATION": "cross_domain_accounting_mismatch",
    "FRONT_RUNNING_MEV": "cross_domain_accounting_mismatch",
    "DOS_LIVENESS": "systemic_liveness_failure",
    "ORACLE_PRICING": "cross_domain_accounting_mismatch",
    "SHARE_ROUNDING_PRECISION": "local_misprice",
    "REWARDS_CLAIMS": "permanent_reward_loss",
    "STATE_MACHINE_LIFECYCLE": "statemachine_terminal_failure",
    "EXTERNAL_INTEGRATION": "cross_domain_accounting_mismatch",
    "UNKNOWN_OTHER": "local_misprice",
}

_TOKEN = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+")


def _tokens(s: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(s or "")]


def _run(cmd: list[str]) -> tuple[int, str, str]:
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def _load(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def replay(audit_id: str, out_dir: Path, quiet: bool = False) -> dict:
    audit = ROOT / "audits" / audit_id
    manifest = audit / "output" / "coverage_manifest.json"
    if not manifest.exists():
        raise SystemExit(f"[p276] no coverage_manifest for {audit_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    acct = out_dir / "accounting_checkpoint.json"
    state = out_dir / "state_transition_checkpoint.json"
    _run([sys.executable, str(SCRIPTS / "accounting_checkpoint_audit.py"),
          "--manifest", str(manifest), "--out", str(acct), "--quiet"])
    _run([sys.executable, str(SCRIPTS / "state_transition_checkpoint_audit.py"),
          "--manifest", str(manifest), "--out", str(state), "--quiet"])

    shadow = out_dir / "shadow"
    rc, so, se = _run([sys.executable, str(RESEARCH / "recall_first_harness.py"),
                       "--manifest", str(manifest), "--accounting", str(acct),
                       "--state-transition", str(state), "--out-dir", str(shadow),
                       "--mode", "shadow", "--quiet"])
    cand_path = shadow / "recall_advisory_candidates.json"
    cands = (_load(cand_path) or {}).get("advisory_candidates", [])

    # ---- auto-build P273 coverage input from harness candidates (locus name tokens = class signals) ----
    cov_in = {"candidates": []}
    for i, c in enumerate(cands):
        sig = _tokens(c.get("contract", "")) + _tokens(c.get("function", ""))
        # add mechanism template hints (already source-derived) to thicken the signal
        for m in c.get("generated_mechanisms", []) or []:
            sig += _tokens(m.get("mechanism_summary", ""))[:6]
        cov_in["candidates"].append({
            "id": c.get("candidate_id") or f"c{i}",
            "locus": c.get("locus"),
            "signals": sig[:24],
            "recall_delta": (c.get("prioritizer_score") or 0) >= 5,
            "impact_supported": True,
        })
    cov_in_path = out_dir / "coverage_candidates.json"
    cov_in_path.write_text(json.dumps(cov_in, indent=1))
    cov_out = out_dir / "coverage_decisions.json"
    _run([sys.executable, str(RESEARCH / "award_class_coverage_router.py"),
          "--candidates", str(cov_in_path), "--out", str(cov_out), "--quiet"])
    cov = _load(cov_out) or {}

    # ---- auto-build P269 triage input from coverage handoff ----
    cls_by_id = {d["id"]: d["award_class"] for d in cov.get("decisions", [])}
    handoff = cov.get("handoff_queue_to_p269", [])
    tri_in = {"candidates": []}
    for cid in handoff:
        cls = cls_by_id.get(cid, "UNKNOWN_OTHER")
        tri_in["candidates"].append({
            "id": cid, "subsystem": cid.split(":")[1] if ":" in str(cid) else cid,
            "award_class": cls,
            "impact_class": _CLASS_TO_IMPACT.get(cls, "local_misprice"),
            "value_at_risk": "multi_user", "terminality": "repeatable",
            "impact_supported": True, "poc_feasibility": "heavy", "feasibility_blockers": [],
            "recall_delta": True,
        })
    tri_in_path = out_dir / "triage_candidates.json"
    tri_in_path.write_text(json.dumps(tri_in, indent=1))
    tri_out = out_dir / "triage_decisions.json"
    _run([sys.executable, str(RESEARCH / "impact_first_poc_triage.py"),
          "--candidates", str(tri_in_path), "--out", str(tri_out), "--quiet"])
    tri = _load(tri_out) or {}

    bundle = {
        "label": LABEL, "mode": "SUPERVISED_EVAL_PASS_A", "audit_id": audit_id,
        "is_gate": False, "research_only": True, "emits_findings": False,
        "advisory_candidate_count": len(cands),
        "advisory_candidates": [{"id": c.get("candidate_id"), "locus": c.get("locus"),
                                 "contract": c.get("contract"), "function": c.get("function"),
                                 "prioritizer_score": c.get("prioritizer_score"),
                                 "mechanisms": len(c.get("generated_mechanisms", []) or [])} for c in cands],
        "coverage_handoff": handoff,
        "coverage_classes": sorted({d["award_class"] for d in cov.get("decisions", [])
                                    if d.get("label", "").startswith("COVERAGE_SELECT")}),
        "coverage_guard": cov.get("guard_violations"),
        "triage_selected": [d["id"] for d in tri.get("decisions", []) if d.get("outcome", "").startswith("SELECT_FOR")],
        "triage_guard": tri.get("guard_violations"),
    }
    (out_dir / "replay_bundle.json").write_text(json.dumps(bundle, indent=1))
    if not quiet:
        print(f"[p276] {audit_id}: cands={len(cands)} classes={bundle['coverage_classes']} "
              f"triage={len(bundle['triage_selected'])}")
    return bundle


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-id", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    replay(a.audit_id, Path(a.out_dir), a.quiet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
