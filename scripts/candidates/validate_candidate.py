"""
validate_candidate.py — Stage-1 candidate validation (gates 1-3): RAW_CANDIDATE -> CONTEXT_MAPPED.

Loads a real detector candidate (from a detector `*_audit.json` `candidates[]` matched by lens_id, or an evidence
bundle / frozen corpus `bundles[]` matched by candidate_id), runs source_resolve -> reachability -> context_map,
and writes validation artifacts under documentation/research/candidates/<audit_id>/<candidate_hash>/.

STOPS at CONTEXT_MAPPED. Never generates a PoC, a report, a poc_ready/report_ready lock, or promotes further.
Refuses to overwrite a folder holding an illustrative fixture unless --force.

Usage:
  python scripts/candidates/validate_candidate.py \
    --candidate-id "<id>" --audit-id "<audit>" --candidate-json "<path>" \
    --target-root "audits/<audit>/contracts/<repo>" --mode strict [--force]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))  # scripts/ for any shared imports

import artifacts as A  # noqa: E402
import policy as P  # noqa: E402
from gates import source_resolve_gate, reachability_gate, context_map_gate  # noqa: E402
from gates import defense_map_gate, invariant_gate  # noqa: E402

TOOL = "scripts/candidates/validate_candidate.py"


# --------------------------------------------------------------- candidate loading
def _lens_id(candidate_id: str) -> str:
    parts = candidate_id.split(":")
    return ":".join(parts[1:4]) if len(parts) >= 4 else ""


def load_candidate(candidate_json: Path, candidate_id: str) -> Optional[Dict[str, Any]]:
    data = json.loads(Path(candidate_json).read_text(encoding="utf-8"))
    # evidence bundle / frozen corpus
    if isinstance(data, dict) and isinstance(data.get("bundles"), list):
        for b in data["bundles"]:
            if b.get("candidate_id") == candidate_id:
                surf = b.get("candidate_surface", "")
                contract, _, func = surf.partition(".")
                loc = b.get("location", {}) or {}
                return {
                    "detector": b.get("detector"), "contract": contract, "function": func,
                    "candidate_surface": surf, "file": loc.get("file"), "line": loc.get("start_line"),
                    "confidence": b.get("confidence"), "declared_severity_potential": b.get("declared_severity_potential"),
                    "rationale": b.get("rationale"), "evidence_signals": b.get("evidence_signals", {}),
                    "visibility": b.get("visibility"), "manifest_id": b.get("manifest_id"), "in_scope": True,
                }
    # detector audit output
    if isinstance(data, dict) and isinstance(data.get("candidates"), list):
        lid = _lens_id(candidate_id)
        for c in data["candidates"]:
            if c.get("lens_id") == lid or c.get("candidate_id") == candidate_id:
                flr = c.get("file_line_refs", "")
                line = None
                if isinstance(flr, str) and ":" in flr:
                    try:
                        line = int(flr.rsplit(":", 1)[1])
                    except ValueError:
                        line = None
                return {
                    "detector": data.get("lens") or candidate_id.split(":")[0],
                    "contract": c.get("contract"), "function": c.get("function"),
                    "candidate_surface": f'{c.get("contract")}.{c.get("function")}',
                    "file": c.get("file"), "line": line,
                    "confidence": c.get("confidence"), "declared_severity_potential": None,
                    "rationale": c.get("reason"),
                    "evidence_signals": {k: c.get(k) for k in
                                         ("invariant_terms", "evidence_terms", "multicall_function",
                                          "check_location", "callable_state_mutators") if c.get(k) is not None},
                    "visibility": c.get("visibility"), "manifest_id": c.get("manifest_id"),
                    "in_scope": bool(c.get("in_scope", True)),
                }
    return None


def load_candidate_from_folder(folder: Path, candidate_id: str) -> Optional[Dict[str, Any]]:
    """Reconstruct the candidate input from already-written Stage-1 artifacts (for Stage-2 re-runs without
    re-supplying the detector json)."""
    m = A.load_existing(folder, "candidate_manifest.json")
    if not m:
        return None
    sr = A.load_existing(folder, "source_resolution.json") or {}
    surf = m.get("candidate_surface", "")
    contract, _, func = surf.partition(".")
    loc = m.get("location", {}) or {}
    return {
        "detector": m.get("detector"), "contract": contract, "function": func, "candidate_surface": surf,
        "file": loc.get("file"), "line": loc.get("start_line"), "confidence": m.get("detector_confidence"),
        "declared_severity_potential": m.get("declared_severity_potential"),
        "rationale": None, "evidence_signals": {}, "visibility": m.get("visibility"),
        "manifest_id": m.get("manifest_id"), "in_scope": m.get("in_scope", True),
        "code_snippet": sr.get("code_snippet"),
    }


# --------------------------------------------------------------- run
def validate(candidate_id: str, audit_id: str, candidate_json: Optional[Path], target_root: Optional[str],
             mode: str = "strict", force: bool = False, max_stage: str = "context") -> Dict[str, Any]:
    chash = A.candidate_hash_of(candidate_id)
    folder = A.candidate_dir(audit_id, chash)
    if A.dir_is_illustrative(folder) and not force:
        raise SystemExit(f"refusing to overwrite illustrative fixture at {folder} (pass --force to override)")

    if candidate_json and Path(candidate_json).exists():
        cand = load_candidate(Path(candidate_json), candidate_id)
    else:
        cand = load_candidate_from_folder(folder, candidate_id)
    if cand is None:
        raise SystemExit(f"candidate not found (json={candidate_json}, folder={folder}): {candidate_id}")

    reasons: List[str] = []
    src_root_disp = target_root

    # ---- Gate 1: source_resolve ----
    src_body, s1 = source_resolve_gate.run(cand, target_root)
    source_hash = src_body.get("source_hash")
    if src_body.get("code_snippet"):
        cand["code_snippet"] = src_body["code_snippet"]
    reasons.append(f"source_resolve -> {s1}")

    reach_body: Optional[Dict[str, Any]] = None
    callable_surface: Optional[Dict[str, Any]] = None
    state_mut: Optional[Dict[str, Any]] = None
    s2 = s3 = None

    if s1 == "RESOLVED_SOURCE":
        # ---- Gate 2: reachability ----
        reach_body, s2 = reachability_gate.run(cand, target_root)
        reasons.append(f"reachability -> {s2} ({reach_body.get('reachability_verdict')})")
        if s2 == "REACHABLE":
            # ---- Gate 3: context_map (restrict callable surface to the real facade contract) ----
            facade_files = sorted({e["file"] for e in reach_body.get("entrypoints", [])
                                   if e.get("is_external_facade") and not e.get("is_interface_decl")}) or None
            callable_surface, state_mut, s3 = context_map_gate.run(cand, target_root, facade_files=facade_files)
            reasons.append(f"context_map -> {s3}")

    # ---- Stage 2 (gates 4-5), only when requested and stage 1 reached CONTEXT_MAPPED ----
    defense_body: Optional[Dict[str, Any]] = None
    invariant_body: Optional[Dict[str, Any]] = None
    s4 = s5 = None
    if max_stage == "invariant" and s3 == "CONTEXT_MAPPED":
        defense_body, s4 = defense_map_gate.run(cand, target_root, reach_body, callable_surface, state_mut)
        reasons.append(f"defense_map -> {s4}")
        if s4 == "DEFENSE_MAPPED":
            invariant_body, s5 = invariant_gate.run(cand, target_root, state_mut, defense_body)
            reasons.append(f"invariant -> {s5}")

    # ---- determine final lifecycle state ----
    if s1 in ("KILLED", "NEEDS_CONTEXT"):
        final_state = s1
    elif s2 in ("KILLED",):
        final_state = "KILLED"
    elif s2 == "NEEDS_CONTEXT" or s2 is None:
        final_state = "NEEDS_CONTEXT"
    elif s3 != "CONTEXT_MAPPED":
        final_state = "NEEDS_CONTEXT"
    elif max_stage != "invariant":
        final_state = "CONTEXT_MAPPED"
    elif s4 == "KILLED":
        final_state = "KILLED"
    elif s4 != "DEFENSE_MAPPED":
        final_state = "NEEDS_CONTEXT"
    elif s5 == "INVARIANT_ANALYZED":
        final_state = "INVARIANT_ANALYZED"
    else:
        final_state = "NEEDS_CONTEXT"

    terminal = final_state in ("KILLED", "NEEDS_CONTEXT")
    pol = P.load_policy()

    def hdr(status: str, extra_reasons: Optional[List[str]] = None) -> Dict[str, Any]:
        return A.common_header(candidate_id=candidate_id, audit_id=audit_id, candidate_hash=chash, tool=TOOL,
                               source_root=src_root_disp, source_hash=source_hash,
                               evidence_refs=[cand.get("file") and f'{cand["file"]}:{cand.get("line")}'] if cand.get("file") else [],
                               status=status, reasons=extra_reasons or [])

    # ---- write artifacts (overwrite-per-candidate) ----
    folder.mkdir(parents=True, exist_ok=True)

    manifest = hdr("PASS")
    manifest.update({
        "detector": cand.get("detector"), "detector_version": "v1",
        "detector_confidence": cand.get("confidence"),
        "declared_severity_potential": cand.get("declared_severity_potential"),
        "candidate_surface": cand.get("candidate_surface"),
        "location": {"file": cand.get("file"), "start_line": cand.get("line")},
        "manifest_id": cand.get("manifest_id"), "visibility": cand.get("visibility"),
        "in_scope": cand.get("in_scope", True),
        "lifecycle_state": final_state,
        "outcome": final_state if terminal else None,
    })
    A.write_json(folder, "candidate_manifest.json", manifest)

    sr = hdr(s1, [src_body.get("resolution_status", "")])
    sr.update(src_body)
    A.write_json(folder, "source_resolution.json", sr)

    if reach_body is not None:
        rb = hdr(s2, [reach_body.get("reason", "")])
        rb.update(reach_body)
        A.write_json(folder, "reachability_map.json", rb)
    if callable_surface is not None:
        cs = hdr("PASS")
        cs.update(callable_surface)
        A.write_json(folder, "callable_surface.json", cs)
    if state_mut is not None:
        sm = hdr("PASS")
        sm.update(state_mut)
        A.write_json(folder, "state_mutation_map.json", sm)

    # ---- Stage 2 artifacts ----
    if defense_body is not None:
        db = hdr(s4, [defense_body.get("summary_plain_english", "")])
        db.update(defense_body)
        A.write_json(folder, "defense_map.json", db)
    if invariant_body is not None:
        ib = hdr(s5, [invariant_body.get("summary_plain_english", "")])
        ib.update(invariant_body)
        A.write_json(folder, "invariant_analysis.json", ib)

    reached_invariant = final_state == "INVARIANT_ANALYZED"
    stage = "stage2_gates_4_5" if max_stage == "invariant" else "stage1_gates_1_3"

    # ---- validation scorecard (4 confidences separated; later gates still null) ----
    attacker_reachable = reach_body.get("attacker_can_reach") if reach_body else None
    validation_confidence = ("medium" if final_state in ("CONTEXT_MAPPED", "INVARIANT_ANALYZED")
                             else "low" if final_state == "NEEDS_CONTEXT" else "none")
    scorecard = hdr("PASS")
    scorecard.update({
        "required": {
            "source_resolved": s1 == "RESOLVED_SOURCE",
            "attacker_reachable": attacker_reachable,
            "in_scope": bool(cand.get("in_scope", True)),
            "context_mapped": s3 == "CONTEXT_MAPPED",
            "defense_mapped": s4 == "DEFENSE_MAPPED",
            "invariant_defined": reached_invariant,
            "defense_bypassed_or_missing": None, "concrete_sequence": None,
            "measurable_impact": None, "testable_locally": None, "no_kill_condition_found": None,
        },
        "confidences": {
            "detector_confidence": cand.get("confidence"),
            "validation_confidence": validation_confidence,
            "exploit_confidence": None,   # no concrete sequence yet
            "impact_confidence": None,    # no measurable harm established yet
        },
        "context_summary": (state_mut or {}).get("term_reference_counts") if state_mut else None,
        "invariant_coverage_conclusion": (invariant_body or {}).get("sufficient_or_incomplete") if invariant_body else None,
        "hard_blockers": (defense_body or {}).get("hard_blockers", []),
        "stage": stage,
    })
    A.write_json(folder, "validation_scorecard.json", scorecard)

    # ---- promotion decision (STOP at the reached state; no PoC/report) ----
    next_gate = (pol.get("next_required_gate_after_invariant", "sequence_gate") if reached_invariant
                 else pol.get("next_required_gate", "defense_map_gate"))
    promo = hdr("PASS")
    promo.update({
        "from_state": "RAW_CANDIDATE",
        "to_state": final_state,
        "current_state": final_state,
        "decided_by": "validate_candidate.py",
        "next_required_gate": next_gate,
        "poc_allowed": False,
        "report_allowed": False,
        "rationale": "; ".join(reasons),
    })
    A.write_json(folder, "promotion_decision.json", promo)

    # ---- verdict.md ----
    stage_label = "Stage-2 validation (gates 1-5)" if max_stage == "invariant" else "Stage-1 validation (gates 1-3)"
    vd = [
        f"# Verdict — {cand.get('candidate_surface')}",
        "", f"**State:** {final_state}  ·  next gate: {next_gate}", "",
        f"{stage_label}. **PoC creation and report drafting are NOT allowed** "
        "(poc_allowed=false, report_allowed=false). This is not a severity/validity/exploit verdict.", "",
        "## Gate results",
    ]
    vd.append(f"- source_resolve: {s1}")
    if s2 is not None:
        vd.append(f"- reachability: {s2} ({(reach_body or {}).get('reachability_verdict')})")
    if s3 is not None:
        vd.append(f"- context_map: {s3}")
    if s4 is not None:
        vd.append(f"- defense_map: {s4}")
    if s5 is not None:
        vd.append(f"- invariant: {s5}")
    if invariant_body is not None:
        vd += ["", "## Invariant coverage (hypothesis, not a bug)",
               invariant_body.get("candidate_risk_statement", "")]
    if final_state == "NEEDS_CONTEXT":
        vd += ["", "## Why not advanced", "; ".join(reasons)]
    if final_state == "KILLED":
        vd += ["", "## Kill reason", "; ".join(reasons)]
    A.write_text(folder, "verdict.md", "\n".join(vd) + "\n")

    return {"final_state": final_state, "folder": str(folder),
            "artifacts": sorted(p.name for p in folder.glob("*"))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-id", required=True)
    ap.add_argument("--audit-id", required=True)
    ap.add_argument("--candidate-json", default="", help="detector audit json or evidence bundle; empty to reconstruct from the candidate folder")
    ap.add_argument("--target-root", default=None)
    ap.add_argument("--mode", default="strict", choices=["strict", "lenient"])
    ap.add_argument("--max-stage", default="context", choices=["context", "invariant"],
                    help="context = gates 1-3 (CONTEXT_MAPPED); invariant = gates 1-5 (INVARIANT_ANALYZED)")
    ap.add_argument("--force", action="store_true", help="overwrite an illustrative fixture folder")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    cj = Path(a.candidate_json) if a.candidate_json else None
    res = validate(a.candidate_id, a.audit_id, cj, a.target_root, a.mode, a.force, a.max_stage)
    if not a.quiet:
        print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
