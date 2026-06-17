#!/usr/bin/env python3
"""impact_direction_gate.py — Phase-23/25 RESEARCH-ONLY post-discovery impact-direction & fix-polarity gate.

Takes a LOCATED root cause and derives the correct FIX POLARITY via a general counterfactual engine, fixing the
Phase-22 failure (located asymmetry -> wrong fix polarity). Phase 25 expands the engine from guard-only to multiple
polarity FAMILIES (guard / value-threshold / index-calldata / state-lifecycle / dos-revert).

ENGINE, NOT LOOKUP (hard rules):
  - `asymmetry.type` ROUTES to a family, but polarity selection requires `objective_defect_facts` + a directional
    counterfactual — type alone never decides.
  - Missing / contradictory facts => NEEDS_PROOF or ABSTAIN; never a guessed polarity.
  - Unknown / malformed `asymmetry.type` => ABSTAIN; it MUST NOT silently default to guard.
  - DoS conservative: code-structural DoS may emit a polarity; economic/cost-asymmetry DoS ABSTAINS unless a
    concrete code-level correction is supplied.
  - Severity is an advisory band (Immunefi v2.2 ceiling) + requires_scope_mapping; NEVER upgraded just because a
    family matched. Every result carries a reason triplet (family_match / invariant_restoration / rejected_alts).

Lineage: research-track instance of the submission/exploitability reasoning (reuses submission/gates/_common). NOT
the coherence judge, NOT a human-label row. HYPOTHESIS-only, human_approval_required:true, un-wired.

  is_gate:false  research_only:true  routes_in_production:false  routed_manifest_ids:[]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "submission" / "gates"))
import _common as SUB  # reuse Immunefi-v2.2 IMPACT_SEVERITY_CEILING + SEVERITY_RANK  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}

SEVERITY_BAND = {
    "fund_loss": ["High", "Critical"], "governance_takeover": ["High", "Critical"],
    "accounting_corruption": ["Medium", "High"], "reward_extraction": ["Medium", "High"],
    "fund_freeze": ["Medium", "High"], "liveness_failure": ["Low", "Medium"],
    "dos": ["Low", "Medium"], "info": ["Informational", "Informational"],
}

# ---- guard family helpers (Phase-23) ----
MUST_BE_LIVE = {
    "paused": {"refund_revert", "admin_rescue"},
    "normal": {"inbound_exec", "refund_revert", "outbound_transfer", "admin_rescue"},
    "liquidating": {"admin_rescue", "refund_revert"},
}
EMERGENCY_GUARD_FOR_STATE = {"paused": "whennotpaused"}
VERDICT_STATUS = SUB._STATUS_FOR_VERDICT


def _has_guard(path, guard):
    return guard.lower() in [g.lower() for g in (path.get("current_guards") or [])]


def _callable_in_state(path, state):
    eg = EMERGENCY_GUARD_FOR_STATE.get(state)
    if eg and _has_guard(path, eg):
        return False
    if state == "normal" and path.get("dead_in_normal"):
        return False
    return True


def _simulate(paths, candidate):
    out = []
    for p in paths:
        q = {**p, "current_guards": list(p.get("current_guards") or [])}
        act, tgt, guard = candidate["action"], candidate.get("target"), candidate.get("guard", "")
        if q["name"] == tgt:
            if act in ("add_guard", "move_guard_to") and guard and not _has_guard(q, guard):
                q["current_guards"].append(guard)
            elif act in ("remove_guard", "move_guard_from"):
                q["current_guards"] = [g for g in q["current_guards"] if g.lower() != guard.lower()]
            elif act == "correct_basis":
                q["dead_in_normal"] = False
        out.append(q)
    return out


def _live_requirements_ok(paths, state):
    need = MUST_BE_LIVE.get(state, set())
    roles = {p["role"] for p in paths}
    for role in need & roles:
        if not any(p["role"] == role and _callable_in_state(p, state) for p in paths):
            return False, role
    return True, None


def _abstain(reason, status="ABSTAIN"):
    return None, [], {"family_match_reason": reason, "invariant_restoration_reason": "", "rejected_alternatives": [],
                      "resolution": status}


# ============================ FAMILY SUB-ENGINES ============================
# each returns (chosen | None, tested[], reasons{}). chosen = {polarity, family, target}.

def _eng_guard(finding, asym, facts):
    paths = finding.get("paths") or []
    gclass = asym.get("guard_class", "emergency_pause")
    state = finding.get("state_condition", {}).get("emergency_state", "normal")
    present, absent = asym.get("present_on", []), asym.get("absent_on", [])
    wrong = asym.get("wrong_basis_on", [])
    if not paths or not (present or absent or wrong):
        return _abstain("guard family: missing paths/present_on/absent_on/wrong_basis_on", "NEEDS_PROOF")
    cands = []
    if asym["type"] == "guard_presence":
        cands += [{"action": "add_guard", "target": t, "guard": asym.get("guard", "")} for t in absent]
        cands += [{"action": "remove_guard", "target": t, "guard": asym.get("guard", "")} for t in present]
        for mt in asym.get("move_to", []):       # move_guard only when a destination fact is supplied
            cands.append({"action": "move_guard", "target": mt, "guard": asym.get("guard", ""),
                          "from": present[0] if present else None})
        if asym.get("conditional_state"):        # make_conditional only when a state fact is supplied
            cands.append({"action": "make_conditional", "target": present[0] if present else (absent[0] if absent else None),
                          "guard": asym.get("guard", ""), "state": asym["conditional_state"]})
    elif asym["type"] == "guard_basis":
        cands += [{"action": "correct_basis", "target": t, "guard": asym.get("guard", "")} for t in wrong]
    tested, chosen, rejected = [], None, []
    for c in cands:
        if c["action"] == "make_conditional":
            verdict, why = "accept", f"apply {c['guard']} only in {c['state']} so other states stay live"
        elif c["action"] == "move_guard":
            sim = _simulate(_simulate(paths, {"action": "move_guard_from", "target": c.get("from"), "guard": c["guard"]}),
                            {"action": "move_guard_to", "target": c["target"], "guard": c["guard"]})
            ok, role = _live_requirements_ok(sim, state)
            verdict, why = ("accept", "move preserves live paths") if ok else ("reject", f"move re-breaks live role '{role}' in '{state}'")
        else:
            sim = _simulate(paths, c)
            ok, role = _live_requirements_ok(sim, state)
            bug_fixed = _callable_in_state(next((p for p in sim if p["name"] == c["target"]), {}), "normal") if asym["type"] == "guard_basis" else True
            if not ok:
                verdict, why = "reject", f"breaks required-live role '{role}' in state '{state}'"
            elif gclass == "access_control" and c["action"] == "remove_guard":
                verdict, why = "reject", "removing an access-control guard never restores a trust boundary"
            elif not bug_fixed:
                verdict, why = "reject", "does not restore the dead path"
            else:
                verdict, why = "accept", "preserves all required-live paths and fixes the located issue"
        tested.append({**c, "counterfactual_verdict": verdict, "reason": why})
        if verdict == "accept" and chosen is None:
            chosen = {"polarity": c["action"], "family": "guard", "target": c["target"]}
        elif verdict == "reject":
            rejected.append(f"{c['action']}->{c['target']}: {why}")
    if not chosen:
        return _abstain("guard family: no candidate preserves required-live paths", "NEEDS_PROOF")
    return chosen, tested, {
        "family_match_reason": f"sibling guard {asym['type']} ({gclass})",
        "invariant_restoration_reason": next(t["reason"] for t in tested if t["counterfactual_verdict"] == "accept"),
        "rejected_alternatives": rejected}


_HARM = {"unwanted_revert", "unwanted_allow"}


def _eng_value(finding, asym, facts):
    op, exp = facts.get("operator"), facts.get("expected_operator")
    harm = facts.get("harm_direction")
    bound_kind = facts.get("bound_kind")  # "missing" | "too_loose" | "too_strict" | "wrong_constant"
    if harm not in _HARM and not bound_kind:
        return _abstain("value family: need harm_direction (unwanted_revert|unwanted_allow) or bound_kind", "NEEDS_PROOF")
    rejected = []
    if op and exp:
        pol = "correct_comparison"
        inv = f"replace operator '{op}' with '{exp}' so the boundary {('stops reverting' if harm=='unwanted_revert' else 'stops accepting the bad value')}"
        rejected = [f"tighten_bound: would worsen unwanted_revert" if harm == "unwanted_revert" else "relax_bound: would keep accepting the bad value"]
    elif bound_kind == "missing":
        pol, inv = "add_bound", "add the absent bound so out-of-range values are rejected"
        rejected = ["correct_comparison: no operator to correct (bound absent)"]
    elif bound_kind == "too_strict" or harm == "unwanted_revert":
        pol, inv = "relax_bound", "loosen the over-strict bound that forces legitimate calls to revert"
        rejected = ["tighten_bound: opposite direction; would worsen the revert"]
    elif bound_kind == "too_loose" or harm == "unwanted_allow":
        pol, inv = "tighten_bound", "tighten the over-permissive bound that accepts a bad value"
        rejected = ["relax_bound: opposite direction; would keep accepting the bad value"]
    elif bound_kind == "wrong_constant":
        pol, inv = "correct_value", "set the constant to its intended value"
        rejected = ["add_bound: a bound exists; the constant is wrong"]
    else:
        return _abstain("value family: facts present but not resolvable to a direction", "NEEDS_PROOF")
    return ({"polarity": pol, "family": "value_threshold", "target": finding.get("function")},
            [{"polarity": pol, "counterfactual_verdict": "accept", "reason": inv}],
            {"family_match_reason": f"value/threshold defect (op={op},exp={exp},bound={bound_kind},harm={harm})",
             "invariant_restoration_reason": inv, "rejected_alternatives": rejected})


def _eng_index(finding, asym, facts):
    defect = facts.get("defect")
    m = {"off_by_one_length": "correct_index", "missing_length_check": "validate_length",
         "unchecked_offset": "validate_offset", "malformed_input_accepted": "reject_malformed_input"}
    if defect not in m:
        return _abstain(f"index/calldata family: need defect in {sorted(m)}", "NEEDS_PROOF")
    inv = {"off_by_one_length": "fix the length math (end-start needs +1) so full-width params don't revert",
           "missing_length_check": "add the length check so out-of-range reads are rejected",
           "unchecked_offset": "validate the offset before indexing",
           "malformed_input_accepted": "reject malformed input that currently passes"}[defect]
    return ({"polarity": m[defect], "family": "index_calldata", "target": finding.get("function")},
            [{"polarity": m[defect], "counterfactual_verdict": "accept", "reason": inv}],
            {"family_match_reason": f"calldata/index defect '{defect}'", "invariant_restoration_reason": inv,
             "rejected_alternatives": [f"{p}: defect is '{defect}', not its trigger" for p in m.values() if p != m[defect]]})


def _eng_state(finding, asym, facts):
    defect = facts.get("defect")
    m = {"redundant_check_blocks_path": "remove_redundant_check", "missing_emergency_path": "allow_emergency_path",
         "unsafe_normal_path": "block_unsafe_normal_path", "recovery_path_blocked": "preserve_recovery_path"}
    if defect not in m:
        return _abstain(f"state/lifecycle family: need defect in {sorted(m)}", "NEEDS_PROOF")
    inv = {"redundant_check_blocks_path": "remove the redundant check that blocks a legitimate lifecycle transition",
           "missing_emergency_path": "allow the emergency path that is currently unreachable",
           "unsafe_normal_path": "block the unsafe path in normal state",
           "recovery_path_blocked": "keep the recovery path callable"}[defect]
    return ({"polarity": m[defect], "family": "state_lifecycle", "target": finding.get("function")},
            [{"polarity": m[defect], "counterfactual_verdict": "accept", "reason": inv}],
            {"family_match_reason": f"state/lifecycle defect '{defect}'", "invariant_restoration_reason": inv,
             "rejected_alternatives": [f"{p}: defect is '{defect}', not its trigger" for p in m.values() if p != m[defect]]})


def _eng_dos(finding, asym, facts):
    dclass = facts.get("dos_class")
    code_fix = facts.get("code_level_correction")
    m = {"unbounded_loop": "avoid_unbounded_loop", "forced_revert": "prevent_forced_revert",
         "external_failure_propagation": "isolate_external_failure"}
    if dclass in m:
        inv = {"unbounded_loop": "bound/paginate the loop so it cannot exhaust gas",
               "forced_revert": "prevent the attacker-forced revert path",
               "external_failure_propagation": "isolate the external call failure"}[dclass]
        return ({"polarity": m[dclass], "family": "dos_revert", "target": finding.get("function")},
                [{"polarity": m[dclass], "counterfactual_verdict": "accept", "reason": inv}],
                {"family_match_reason": f"code-structural DoS '{dclass}'", "invariant_restoration_reason": inv,
                 "rejected_alternatives": []})
    if dclass == "economic_cost_asymmetry":
        if code_fix:
            return ({"polarity": "isolate_external_failure", "family": "dos_revert", "target": finding.get("function")},
                    [{"polarity": "code_level_correction", "counterfactual_verdict": "accept", "reason": str(code_fix)}],
                    {"family_match_reason": "economic DoS WITH a concrete code-level correction",
                     "invariant_restoration_reason": str(code_fix), "rejected_alternatives": []})
        return _abstain("DoS conservative: economic/cost-asymmetry DoS with no concrete code-level correction", "ABSTAIN")
    return _abstain(f"dos family: need dos_class in {sorted(m)+['economic_cost_asymmetry']}", "NEEDS_PROOF")


_DISPATCH = {"guard_presence": _eng_guard, "guard_basis": _eng_guard,
             "value_boundary": _eng_value, "comparison": _eng_value, "threshold": _eng_value,
             "index_handling": _eng_index, "lifecycle_check": _eng_state, "dos": _eng_dos}


def evaluate_polarity(finding):
    asym = finding.get("asymmetry") or {}
    t = asym.get("type")
    facts = finding.get("objective_defect_facts", {})
    fn = _DISPATCH.get(t)
    if fn is None:  # unknown/malformed -> ABSTAIN, never guard default
        return _abstain(f"unknown/malformed asymmetry.type '{t}' — abstain (no silent guard default)")
    return fn(finding, asym, facts)


def run(finding):
    if not finding.get("asymmetry"):
        return ({"status": "NEEDS_CONTEXT", "reason": "missing asymmetry structured input", **FLAGS}, "NEEDS_CONTEXT")
    chosen, tested, reasons = evaluate_polarity(finding)
    impact_class = finding.get("proposed_impact_class", "info")
    band = SEVERITY_BAND.get(impact_class, ["Informational", "Informational"])  # NEVER bumped by family match
    resolution = reasons.get("resolution", "ANALYZED")
    verdict = SUB.WARN if chosen else SUB.NEEDS_PROOF
    body = {
        **FLAGS, "tool": "impact_direction_gate.py", "candidate_id": finding.get("candidate_id"),
        "contract": finding.get("contract"), "function": finding.get("function"),
        "hypothesis_status": "HYPOTHESIS_UNCONFIRMED", "human_approval_required": True,
        "actor": finding.get("actor"), "state_condition": finding.get("state_condition"),
        "direction_of_failure": finding.get("direction_of_failure"), "harmed_party": finding.get("harmed_party"),
        "impact_on_asset_control": {"proposed_impact_class": impact_class, "severity_band": band,
                                    "proposed_severity_ceiling": band[1],
                                    "ceiling_reason": "depends on recoverability, affected assets, and privileged recovery options",
                                    "requires_scope_mapping": True,
                                    "note": "advisory band (Immunefi v2.2 ceiling); NEVER upgraded by family match; "
                                            "point severity needs scope mapping + PoC"},
        "fix_polarity": chosen or {"polarity": "undetermined", "family": None},
        "family_match_reason": reasons.get("family_match_reason"),
        "invariant_restoration_reason": reasons.get("invariant_restoration_reason"),
        "rejected_alternatives": reasons.get("rejected_alternatives", []),
        "counterfactual": {"tested_candidates": tested,
                           "principle": "type routes the family; polarity needs objective facts + a directional "
                                        "counterfactual; missing/contradictory facts abstain"},
        "evidence_refs": finding.get("evidence_refs", []),
        "advisory_status": (VERDICT_STATUS[verdict] if chosen else
                            ("ABSTAIN" if resolution == "ABSTAIN" else VERDICT_STATUS[SUB.NEEDS_PROOF])),
    }
    blob = json.dumps(body).lower()
    for bad in ("confirmed", "proven", "exploitable", "valid bug", "submit", "guaranteed"):
        if re.search(r"\b" + re.escape(bad) + r"\b", blob):
            raise SystemExit(f"[impact_direction_gate] verdict word '{bad}' leaked into output")
    return body, "IMPACT_DIRECTION_ANALYZED"


# ============================ self-test ============================

def _run_fx(fx):
    b, _ = run(fx)
    fp = b["fix_polarity"]
    return fp.get("family"), fp.get("polarity"), b["advisory_status"], b["impact_on_asset_control"]["severity_band"]


def _self_test():
    ok = True
    cases = [
        # (label, finding, expect_family, expect_polarity_or_None, expect_abstain)
        ("ZetaChain guard emergency-path", {"function": "onReceive", "proposed_impact_class": "fund_freeze",
            "state_condition": {"emergency_state": "paused"},
            "paths": [{"name": "onReceive", "role": "inbound_exec", "current_guards": ["onlyTssAddress"]},
                      {"name": "onRevert", "role": "refund_revert", "current_guards": ["whenNotPaused", "onlyTssAddress"]}],
            "asymmetry": {"type": "guard_presence", "guard": "whenNotPaused", "guard_class": "emergency_pause",
                          "present_on": ["onRevert"], "absent_on": ["onReceive"]}}, "guard", "remove_guard", False),
        ("Decent trust-boundary", {"function": "receiveFromBridge", "proposed_impact_class": "fund_loss",
            "state_condition": {"emergency_state": "normal"},
            "paths": [{"name": "UTB.receiveFromBridge", "role": "inbound_exec", "current_guards": []},
                      {"name": "Adapter.receiveFromBridge", "role": "inbound_exec", "current_guards": ["onlyExecutor"]}],
            "asymmetry": {"type": "guard_presence", "guard": "onlyExecutor", "guard_class": "access_control",
                          "present_on": ["Adapter.receiveFromBridge"], "absent_on": ["UTB.receiveFromBridge"]}},
         "guard", "add_guard", False),
        ("Centrifuge impossible basis", {"function": "execute", "proposed_impact_class": "liveness_failure",
            "state_condition": {"emergency_state": "normal"},
            "paths": [{"name": "execute", "role": "inbound_exec", "current_guards": ["onlyOrigin"], "dead_in_normal": True}],
            "asymmetry": {"type": "guard_basis", "guard": "onlyOrigin", "guard_class": "access_control", "wrong_basis_on": ["execute"]}},
         "guard", "correct_basis", False),
        ("paused() value-boundary tighten", {"function": "paused", "proposed_impact_class": "liveness_failure",
            "asymmetry": {"type": "value_boundary"},
            "objective_defect_facts": {"operator": "<=", "expected_operator": "<", "harm_direction": "unwanted_allow"}},
         "value_threshold", "correct_comparison", False),
        ("Kleidi M-02 calldata index", {"function": "checkCalldata", "proposed_impact_class": "dos",
            "asymmetry": {"type": "index_handling"}, "objective_defect_facts": {"defect": "off_by_one_length"}},
         "index_calldata", "correct_index", False),
        ("Kleidi M-03 redundant lifecycle check", {"function": "_afterCall", "proposed_impact_class": "liveness_failure",
            "asymmetry": {"type": "lifecycle_check"}, "objective_defect_facts": {"defect": "redundant_check_blocks_path"}},
         "state_lifecycle", "remove_redundant_check", False),
        ("Kleidi M-01 economic DoS -> ABSTAIN", {"function": "schedule", "proposed_impact_class": "dos",
            "asymmetry": {"type": "dos"}, "objective_defect_facts": {"dos_class": "economic_cost_asymmetry"}},
         None, None, True),
        ("synthetic unbounded-loop DoS", {"function": "distribute", "proposed_impact_class": "dos",
            "asymmetry": {"type": "dos"}, "objective_defect_facts": {"dos_class": "unbounded_loop"}},
         "dos_revert", "avoid_unbounded_loop", False),
        ("missing facts -> NEEDS_PROOF abstain", {"function": "f", "proposed_impact_class": "info",
            "asymmetry": {"type": "value_boundary"}, "objective_defect_facts": {}}, None, None, True),
        ("malformed type -> ABSTAIN (never guard)", {"function": "f", "proposed_impact_class": "info",
            "asymmetry": {"type": "nonsense_xyz"}}, None, None, True),
    ]
    for label, fx, efam, epol, eabs in cases:
        fam, pol, status, band = _run_fx(fx)
        if eabs:
            good = (pol in (None, "undetermined")) and fam is None
        else:
            good = (fam == efam) and (pol == epol)
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}: family={fam} polarity={pol} status={status}")

    # no-cross-family: a value/index/dos finding must NEVER yield a guard polarity
    cross_ok = True
    for fx in (cases[3][1], cases[4][1], cases[7][1]):
        fam, pol, _, _ = _run_fx(fx)
        if fam == "guard":
            cross_ok = False
    print(f"  [{'PASS' if cross_ok else 'FAIL'}] no-cross-family: non-guard inputs never produce a guard polarity")
    ok &= cross_ok

    # no-inflation: a Low/liveness finding's band ceiling must not be High/Critical
    _, _, _, band = _run_fx(cases[3][1])
    infl_ok = band[1] in ("Low", "Medium")
    print(f"  [{'PASS' if infl_ok else 'FAIL'}] no-inflation: liveness band {band} not H/M")
    ok &= infl_ok

    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--finding")
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if not args.finding:
        ap.error("--finding or --self-test required")
    body, st = run(json.load(open(args.finding)))
    out = args.out or Path(args.finding).with_name(Path(args.finding).stem + "_impact_gate.json")
    Path(out).write_text(json.dumps(body, indent=2))
    print(f"[impact_direction_gate] {st} -> {out}  family={body.get('fix_polarity',{}).get('family')} "
          f"polarity={body.get('fix_polarity',{}).get('polarity')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
