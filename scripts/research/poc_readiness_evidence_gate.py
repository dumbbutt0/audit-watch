#!/usr/bin/env python3
"""P278 — strict PoC-readiness evidence gate (RESEARCH-ONLY, ADVISORY, UN-WIRED).

Applies the 10-point readiness standard to evidence packages. A candidate is READY_FOR_POC_INTENT ONLY if every
readiness dimension is present (non-empty, non-'operator-to-derive'). Otherwise NEEDS_MORE_EVIDENCE (or NEEDS_MORE_
RUNTIME when only runtime-derivable fields remain). Honors the PoC execution budget: at most poc_execution_budget READY
candidates are flagged for runtime; the rest -> DEFER_POC_BUDGET. NEVER sets severity/reportability/submission/
confirmed. Fail-closed on guard violations.

Usage:
  python scripts/research/poc_readiness_evidence_gate.py --packages <evidence_packages.json> --out <report.json> [--quiet]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "config/research_expanded_validation_queue.json").read_text())
LABEL = "SUPERVISED_EVAL"
PLACEHOLDERS = {str(x).strip().lower() for x in CFG["placeholder_markers"]}
REQ = CFG["readiness_required_dimensions"]
FORBIDDEN = ("severity", "reportable", "submission_ready", "concluded", "emits_finding", "production_routing")
# fields that are only resolvable by running a harness (so their absence => NEEDS_MORE_RUNTIME, not _EVIDENCE)
RUNTIME_FIELDS = {"refutation_result", "poc_assertion"}
# P281 READY-gate repair config (source-span guard/state/value classes)
_GCFG = json.loads((ROOT / "config/research_poc_readiness_gate.json").read_text())
VALUE_CLASSES = set(_GCFG["value_classes"])
STATE_CLASSES = set(_GCFG["state_machine_classes"])
# P284 invariant-delta lift: a value/state candidate may pass the value/state block on a SOURCE-BACKED deviation.
_IDCFG = json.loads((ROOT / "config/research_invariant_delta_deriver.json").read_text())
IDD_LIFT = set(_IDCFG["lift_statuses"])


def _id_deviation(pkg: dict) -> bool:
    """True iff a source-backed invariant-delta deviation was found at HIGH|MEDIUM (P284)."""
    ide = pkg.get("invariant_delta_evidence") or {}
    return (ide.get("invariant_delta_status") in IDD_LIFT
            and str(ide.get("confidence", "")).upper() in ("HIGH", "MEDIUM"))
P281_STATUSES = {"INLINE_GUARD_REFUTED", "NEEDS_GUARD_BYPASS_EVIDENCE", "NEEDS_STATE_MACHINE_EVIDENCE",
                 "NEEDS_VALUE_FLOW_EVIDENCE", "NEEDS_SOURCE_SPAN"}
P285_STATUSES = {"NEEDS_GUARD_CONTEXT"}  # P285: ambiguous auth READ (no execution gate) — fail-closed, never lifts
P291_STATUSES = {"NEEDS_INTEGRATION_DEVIATION_EVIDENCE"}  # P291: EXTERNAL_INTEGRATION w/o source-backed deviation
VALID_STATUSES = set(CFG["statuses"]) | P281_STATUSES | P285_STATUSES | P291_STATUSES


def _integration_deviation(pkg: dict) -> bool:
    """P291: True iff a source-backed EXTERNAL_INTEGRATION deviation was found (auto or explicit)."""
    return bool((pkg.get("integration_deviation_evidence") or {}).get("deviation_present") is True)


class FailClosed(Exception):
    pass


def _present(v) -> bool:
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, (list, dict)):
        return len(v) > 0
    s = str(v).strip().lower()
    return s not in PLACEHOLDERS and "operator-to-derive" not in s and "operator to derive" not in s and len(s) > 0


def classify(pkg: dict) -> dict:
    # operator-supplied terminal status overrides (REFUTED / NONAWARDED_TRUE_POSITIVE / SAME_AREA_WRONG_MECHANISM)
    forced = pkg.get("operator_status")
    low_conf_core = []
    # ---- P281 source-span gate (D1-D4): activates ONLY when a real function body was resolvable; otherwise the
    # pre-P281 (manifest-only) path runs unchanged for back-compat with synthetic inputs. ----
    ge = pkg.get("gate_evidence") or {}
    cls = pkg.get("award_class", "")
    p281 = None
    if not forced and ge.get("body_available"):
        if ge.get("is_declaration_only"):
            p281 = "NEEDS_SOURCE_SPAN"  # D4: interface/abstract decl, no body to establish attacker_path
        elif ge.get("inline_guard_detected") and not _present(pkg.get("guard_bypass_evidence")):
            p281 = "INLINE_GUARD_REFUTED"  # D1: inline caller/owner/approval guard, no source-backed bypass
        elif cls in VALUE_CLASSES and not (
                (ge.get("value_flow_detected") and ge.get("value_anomaly_div_before_mul"))
                # P283 V2: OR a bounded cross-function trace that found a real (comment-stripped) anomaly callee.
                or (pkg.get("trace_evidence", {}).get("trace_status") == "TRACE_FOUND"
                    and (pkg.get("trace_evidence", {}).get("value_flow_path") or {}).get("anomaly")
                    and str(pkg.get("trace_evidence", {}).get("value_flow_confidence", "")).upper() in ("HIGH", "MEDIUM"))
                # P284: OR a SOURCE-BACKED invariant-delta deviation (sibling/registry/rounding/oracle) at HIGH|MEDIUM.
                or _id_deviation(pkg)):
            # A value class lifts past this block ONLY with a concrete in-span anomaly OR a concrete cross-function
            # anomaly OR a source-backed corrected-reference deviation. Value-flow PRESENCE alone (in-span or
            # out-of-span wrapper or getter) is NOT enough; neither is a before/after equation with no deviation.
            p281 = "NEEDS_VALUE_FLOW_EVIDENCE"  # D3 / V2 / P284
        elif cls in STATE_CLASSES and not (
                ge.get("state_machine_detected")
                # P284: OR a state-machine value-invariant deviation (forbidden-state mutation).
                or (pkg.get("invariant_delta_evidence", {}).get("invariant_delta_status") == "STATE_MACHINE_DELTA_FOUND")):
            p281 = "NEEDS_STATE_MACHINE_EVIDENCE"  # D2
        elif cls == "EXTERNAL_INTEGRATION" and not _integration_deviation(pkg):
            # P291 Part A: EXTERNAL_INTEGRATION may not lift on the class template alone. Require a source-backed
            # integration deviation (low-level call / callback / reentrancy-ordering / explicit fee-on-transfer etc.).
            p281 = "NEEDS_INTEGRATION_DEVIATION_EVIDENCE"
        elif ge.get("inline_guard_ambiguous") and not _id_deviation(pkg):
            # P285: an auth/ownership token exists but is an AMBIGUOUS read (not in any execution gate) and no
            # source-backed deviation resolves it -> fail-closed: hold for guard context, never lift on this alone.
            p281 = "NEEDS_GUARD_CONTEXT"
    if forced in ("REFUTED", "NONAWARDED_TRUE_POSITIVE", "SAME_AREA_WRONG_MECHANISM", "INCONCLUSIVE"):
        status = forced
        missing = []
    elif p281:
        status, missing = p281, []
    else:
        missing = [f for f in REQ if not _present(pkg.get(f))]
        # P279: if derived-evidence confidence is present, require core fields (attacker_path/impact_delta/
        # victim_gainer) to be HIGH|MEDIUM. LOW-confidence core evidence cannot reach READY (keeps auto-derived
        # READY low-noise). Hand-authored packages without a confidence map are unaffected.
        low_conf_core = []
        dc = pkg.get("derived_confidence")
        if isinstance(dc, dict):
            for core in ("attacker_path", "impact_delta", "victim_gainer"):
                if str((dc.get(core) or {}).get("confidence", "")).upper() not in ("HIGH", "MEDIUM"):
                    low_conf_core.append(core)
        if not missing and not low_conf_core:
            status = "READY_FOR_POC_INTENT"
        elif not missing and low_conf_core:
            status = "NEEDS_MORE_EVIDENCE"
        elif set(missing).issubset(RUNTIME_FIELDS):
            status = "NEEDS_MORE_RUNTIME"
        else:
            status = "NEEDS_MORE_EVIDENCE"
    return {"candidate_id": pkg.get("candidate_id"), "award_class": pkg.get("award_class"),
            "evidence_source": pkg.get("evidence_source"),
            "low_confidence_core": low_conf_core if not forced else [],
            "missing_dimensions": missing, "status": status,
            "p281_block": p281,
            "gate_evidence_summary": {
                "body_available": ge.get("body_available", False),
                "is_declaration_only": ge.get("is_declaration_only", False),
                "inline_guard_detected": ge.get("inline_guard_detected", False),
                "inline_guard_ambiguous": ge.get("inline_guard_ambiguous", False),  # P285
                "guard_contexts": ge.get("guard_contexts", []),                      # P285 read-vs-guard taxonomy
                "guard_markers": ge.get("guard_markers", []),
                "state_machine_detected": ge.get("state_machine_detected", False),
                "or_state_gate": ge.get("or_state_gate", False),
                "value_flow_detected": ge.get("value_flow_detected", False),
                "value_flow_out_of_span": ge.get("value_flow_out_of_span", False),
                "value_anomaly_div_before_mul": ge.get("value_anomaly_div_before_mul", False),
                "value_flow_subreason": (
                    "value_flow_out_of_span(wrapper/delegation)" if ge.get("value_flow_out_of_span")
                    else "no_value_flow_in_span" if not ge.get("value_flow_detected")
                    else "value_flow_present_but_no_anomaly" if not ge.get("value_anomaly_div_before_mul")
                    else "value_flow_with_anomaly") if ge.get("body_available") else None,
                "trace_status": pkg.get("trace_evidence", {}).get("trace_status"),
                "trace_value_flow_confidence": pkg.get("trace_evidence", {}).get("value_flow_confidence"),
                "invariant_delta_status": pkg.get("invariant_delta_evidence", {}).get("invariant_delta_status"),
                "invariant_delta_type": pkg.get("invariant_delta_evidence", {}).get("derivation_type"),
                "invariant_delta_confidence": pkg.get("invariant_delta_evidence", {}).get("confidence"),
                "source_span": ge.get("source_span")},
            # advisory contract — hard-stamped
            "severity": None, "reportable": False, "submission_ready": False, "concluded": False,
            "emits_finding": False, "production_routing": False, "status_kind": "ADVISORY_VALIDATION_DECISION"}


def run(pkgs_path: Path, out_path: Path, quiet: bool) -> int:
    data = _load(pkgs_path)
    if data is None:
        raise FailClosed(f"missing/unreadable packages: {pkgs_path}")
    pkgs = data.get("packages") if isinstance(data, dict) else data
    if not isinstance(pkgs, list):
        raise FailClosed("packages must be a list (or {packages:[...]})")

    decisions = [classify(p) for p in pkgs]
    # PoC execution budget: cap READY flagged-for-runtime; demote extras to DEFER_POC_BUDGET
    budget = CFG["poc_execution_budget"]
    ready = [d for d in decisions if d["status"] == "READY_FOR_POC_INTENT"]
    for d in ready[budget:]:
        d["status"] = "DEFER_POC_BUDGET"

    viol = _guard(decisions)
    guard = {"module": "poc_readiness_evidence_gate", "result": "PASS" if not viol else "FAIL",
             "guard_violations": len(viol), "violations": viol}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    (out_path.parent / "poc_readiness_guard_report.json").write_text(json.dumps(guard, indent=2))
    if viol:
        raise FailClosed(f"GUARD FAILURE: {len(viol)} violation(s)")

    from collections import Counter
    tally = Counter(d["status"] for d in decisions)
    out = {"label": LABEL, "mode": "SUPERVISED_EVAL_POC_READINESS", "is_gate": False, "research_only": True,
           "emits_findings": False, "poc_execution_budget": budget,
           "severe_concluded_or_reportable_fp": 0, "status_tally": dict(tally),
           "ready_for_poc_intent": [d["candidate_id"] for d in decisions if d["status"] == "READY_FOR_POC_INTENT"],
           "decisions": decisions}
    out_path.write_text(json.dumps(out, indent=2))
    if not quiet:
        print(f"[p278:gate] {dict(tally)} | severe_FP=0 guard={guard['result']}")
    return 0


def _guard(decisions: list) -> list:
    viol = []
    for d in decisions:
        if d.get("severity") is not None:
            viol.append({"id": d.get("candidate_id"), "field": "severity"})
        for f in FORBIDDEN:
            if d.get(f) not in (False, None):
                viol.append({"id": d.get("candidate_id"), "field": f})
        if d.get("status") not in VALID_STATUSES:
            viol.append({"id": d.get("candidate_id"), "field": "status", "value": d.get("status")})
    return viol


def _load(p: Path):
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packages", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    try:
        run(Path(a.packages), Path(a.out), a.quiet)
    except FailClosed as e:
        print(f"[poc_readiness_evidence_gate] FAIL-CLOSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
