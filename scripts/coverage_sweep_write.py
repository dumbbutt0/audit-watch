#!/usr/bin/env python3
"""
coverage_sweep_write.py — Validate + apply /coverage-sweep skill decisions to dispositions (no LLM).

Reads data/coverage_sweep/_decisions.json ({"decisions":[...]}) and applies each to
output/coverage_dispositions.json with evidence enforcement:

  cleared              -> disposition 'cleared' (REQUIRES evidence + reason; rejected otherwise)
  deferred_out_of_scope-> disposition 'deferred_out_of_scope' (REQUIRES reason)
  needs_deep_pass      -> disposition 'assigned' (assigned_pass='deep', agent=suggested) — gate still
                          blocks, so a deep specialist must resolve it (no silent clear)
  finding              -> mints a provisional finding (SWP-###) in output/findings_coverage_sweep.json
                          and sets disposition 'finding' with that ref

Never fabricates a clear: a 'cleared' without an evidence span + reason is rejected (the item stays
pending and the gate keeps blocking).

Usage:
    python scripts/coverage_sweep_write.py [--decisions <path>]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import update_coverage_disposition as ucd  # noqa: E402
import dependency_clear_utils as dcu  # noqa: E402
import math_estimator_taxonomy as me  # noqa: E402
import validate_math_estimator_clears as vme  # noqa: E402
import dynamic_weight_lifecycle_taxonomy as dwl  # noqa: E402  (P174 F1 — re-surface only)
import validate_dynamic_weight_lifecycle_clears as vdwl  # noqa: E402
import dependency_metadata as dmeta  # noqa: E402  (P178 — structured dependency evidence capture)
import special_focus_terms as sft  # noqa: E402
import gate_dos_utils as gdu  # noqa: E402
import spec_checklist_utils as scu  # noqa: E402
import validate_spec_checklist_clears as vscc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SWEEP_STATUSES = {"cleared", "finding", "needs_deep_pass", "deferred_out_of_scope"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decisions")
    args = ap.parse_args()

    dec_path = Path(args.decisions) if args.decisions else (audit_path("data/coverage_sweep") / "_decisions.json")
    if not dec_path.exists():
        raise SystemExit(f"[coverage_sweep_write] decisions not found: {dec_path} — run the /coverage-sweep skill first.")
    decisions = json.loads(dec_path.read_text())
    if isinstance(decisions, dict):
        decisions = decisions.get("decisions", [])

    p, data, idx = ucd._load()  # dispositions

    # manifest scores + high-score strong-clear policy
    man_path = audit_path("output") / "coverage_manifest.json"
    score_of: dict[str, int] = {}
    manifest_items: list[dict] = []
    if man_path.exists():
        try:
            manifest_items = json.loads(man_path.read_text()).get("items", [])
            score_of = {i["id"]: i.get("attack_surface_score", 0) for i in manifest_items}
        except (json.JSONDecodeError, OSError):
            pass
    try:
        pol = json.loads((ROOT / "config" / "agent_policy.json").read_text()).get("coverage_policy", {})
    except Exception:
        pol = {}
    strong_on = pol.get("high_score_strong_clear", True)
    strong_threshold = pol.get("high_score_threshold", 3)
    strong_fields = pol.get("strong_clear_fields", ["attacker_reachability", "guard_or_invariant", "no_impact_reason"])
    # dependency-aware clear policy (a clear may not lean on an unreviewed downstream dependency)
    dep_require = pol.get("require_dependency_clear_metadata", True)
    full_audit = os.environ.get("AUDITWATCH_FULL_AUDIT", "").strip().lower() in ("1", "true", "yes", "on")
    dep_strict = pol.get("dependency_clear_strict", False) or (pol.get("dependency_clear_strict_full_audit", True) and full_audit)
    # P177: prose-only / incomplete dependency claims are advisory; hard-route only on complete structured
    # metadata resolving an in-scope unproven guard. Reversible via guarded_downstream_require_structured.
    dep_require_structured = pol.get("guarded_downstream_require_structured", True)
    # locality / path-dominance: a non-local guard must dominate every attacker-reachable path.
    locality_on = pol.get("dependency_locality_strict", False) or (pol.get("dependency_locality_strict_full_audit", True) and full_audit)
    dep_blocking_statuses = dcu.BLOCKING_CLASSIFICATIONS | (dcu.LOCALITY_BLOCKING if locality_on else set())
    cg_path = audit_path("data") / "interactions" / "call_graph.json"
    call_graph = {}
    if cg_path.exists():
        try:
            call_graph = json.loads(cg_path.read_text())
        except (json.JSONDecodeError, OSError):
            call_graph = {}
    name_index = dcu.build_manifest_name_index(manifest_items)
    # math-estimator proof policy (a math-estimator/guard/formula clear needs an independent re-derivation,
    # not NatSpec/code agreement). Layered AFTER the dependency check so dependency enforcement is untouched.
    man_idx = {i["id"]: i for i in manifest_items}
    me_tax = me.load_taxonomy()
    me_require = pol.get("require_math_estimator_proof", True)
    math_strict = me_require and (pol.get("math_estimator_strict", False)
                                  or (pol.get("math_estimator_strict_full_audit", True) and full_audit))
    me_adversarial = pol.get("math_adversarial_proof", True)
    # dynamic-weight lifecycle proof policy (P174 F1; layered AFTER math-estimator, same fail-open/flag-gated
    # style). A clear of a dynamic-weight lifecycle surface (setWeights/update/onSwap/computeBalance) needs a
    # lifecycle-completeness proof (sum/bounds/epsilon/interval/staleness). RE-SURFACE ONLY → needs_deep_pass.
    lc_tax = dwl.load_taxonomy()
    lc_require = pol.get("require_dynamic_weight_lifecycle_proof", True)
    lc_strict = lc_require and (pol.get("dynamic_weight_lifecycle_strict", False)
                                or (pol.get("dynamic_weight_lifecycle_strict_full_audit", True) and full_audit))
    lc_adversarial = pol.get("lifecycle_adversarial_proof", True)
    # special-focus strong-clear policy: a clear on a special-focus surface (gateway/checkpoint/subnet/
    # collateral/signature/queue/value-transfer terms or a high attack-surface score) must carry the deep
    # strong-clear fields, not a thin local explanation. Missing → needs_deep_pass (strict) / warn (advisory).
    sf_on = pol.get("special_focus_strong_clear", True)
    sf_strict = sf_on and (pol.get("special_focus_strong_clear_strict", False)
                           or (pol.get("special_focus_strong_clear_strict_full_audit", True) and full_audit))
    SF_CORE_FIELDS = ["attacker_entrypoint", "cross_function_consumers", "downstream_sinks",
                      "state_transition_ordering", "value_source_consistency"]
    # gate-vs-DoS: a clear that calls a revert/underflow an "intended gate" must carry a liveness disproof
    # (does the same revert block a legitimate actor on a critical path?). Missing → needs_deep_pass.
    gd_on = pol.get("gate_vs_dos_enabled", True)
    gd_strict = gd_on and (pol.get("gate_vs_dos_strict", False)
                           or (pol.get("gate_vs_dos_strict_full_audit", True) and full_audit))
    # anti-false-clear spec checklists (permit/erc4626/callback/oracle-liquidation + reward/slippage/inflation)
    sc_on = pol.get("spec_checklist_enabled", True)
    sc_strict = sc_on and (pol.get("spec_checklist_strict", False)
                           or (pol.get("spec_checklist_strict_full_audit", True) and full_audit))
    # adversarial spec-checklist: a FIELD-COMPLETE checklist of boilerplate ("reviewed; conserves accounting")
    # is rejected as confirmatory (Hybra: 4 awarded reward fns cleared this way). Advisory/normal non-blocking.
    sc_adversarial = sc_on and pol.get("spec_checklist_adversarial", True)
    sc_adv_strict = sc_adversarial and (pol.get("spec_checklist_adversarial_strict", False)
                                        or (pol.get("spec_checklist_adversarial_strict_full_audit", True) and full_audit))
    sc_ctx = scu.build_context(man_idx.values())  # run-level reward-layer / external-market signals

    sweep_findings: list[dict] = []
    applied = {"cleared": 0, "finding": 0, "needs_deep_pass": 0, "deferred_out_of_scope": 0,
               "dependency_downgraded": 0, "math_estimator_downgraded": 0, "special_focus_downgraded": 0,
               "gate_dos_downgraded": 0, "spec_checklist_downgraded": 0, "lifecycle_downgraded": 0}
    rejected: list[str] = []
    swp_n = 0

    for d in decisions:
        mid = d.get("manifest_id")
        sd = d.get("disposition") or d.get("status")
        if mid not in idx:
            rejected.append(f"{mid}: unknown manifest id"); continue
        if sd not in SWEEP_STATUSES:
            rejected.append(f"{mid}: invalid sweep disposition '{sd}'"); continue
        evidence = d.get("evidence") or ([d["evidence_span"]] if d.get("evidence_span") else [])
        reason = d.get("reason") or d.get("clear_reason")

        if sd == "cleared":
            # high-attack-surface items cannot be cheap-cleared: require the strong-clear fields.
            strong = {f: d.get(f) for f in strong_fields}
            if strong_on and score_of.get(mid, 0) >= strong_threshold:
                missing = [f for f in strong_fields if not (strong.get(f) or "").strip()]
                if missing:
                    rejected.append(f"{mid}: high-surface (score {score_of.get(mid)}) clear needs "
                                    f"{', '.join(missing)} — rejected, use needs_deep_pass or a strong clear")
                    continue
            # dependency-aware enforcement: a clear may not lean on an unreviewed downstream dependency,
            # nor on a non-local guard that does not dominate every attacker-reachable path to this item.
            synth = {"status": "cleared", "manifest_id": mid, "clear_reason": reason,
                     "guard_or_invariant": strong.get("guard_or_invariant"),
                     "no_impact_reason": strong.get("no_impact_reason"),
                     "clear_depends_on": d.get("clear_depends_on"),
                     "dependency_clearance_status": d.get("dependency_clearance_status"),
                     "dependency_reason": d.get("dependency_reason"),
                     "dependency_evidence": d.get("dependency_evidence"),
                     "downstream_guard_claim": d.get("downstream_guard_claim"),
                     "downstream_guard_type": d.get("downstream_guard_type"),
                     "guard_locality": d.get("guard_locality"),
                     "path_dominance_evidence": d.get("path_dominance_evidence"),
                     "alternative_paths_considered": d.get("alternative_paths_considered"),
                     # P177 clear-time evidence-capture fields (additive; absent → prior behavior)
                     "dependency_name": d.get("dependency_name"),
                     "dependency_scope": d.get("dependency_scope"),
                     "dependency_status": d.get("dependency_status"),
                     "proof_status": d.get("proof_status")}
            dep_meta: dict = {}
            if dcu.is_dependency_based_clear(synth):
                # P178: auto-capture resolved structured dependency facts from prose+manifest when the clear
                # lacks them (fail-open; RESOLVE-OR-NOTHING → unresolved prose stays advisory). This feeds the
                # UNCHANGED P177 router structured facts; it does not alter the routing rule.
                if not (synth.get("clear_depends_on") and synth.get("dependency_clearance_status")):
                    cap = dmeta.extract_dependency_metadata(synth, manifest_index=man_idx,
                                                            name_index=name_index, disposition_index=idx)
                    if cap.get("dependency_name"):
                        for _k, _v in cap.items():
                            if _v is not None and not synth.get(_k):
                                synth[_k] = _v
                cls = dcu.classify_clear(synth, idx, name_index, manifest_index=man_idx, call_graph=call_graph)
                # P177: prose-only/incomplete → advisory; hard-route only on structured in-scope unproven guard.
                decision = dcu.dependency_route_decision(cls, synth, locality_on=locality_on,
                                                         require_structured=dep_require_structured)
                blocking = decision == "block"
                if blocking and (dep_strict or cls["status"] in dcu.LOCALITY_BLOCKING):
                    # strict: route to needs_deep_pass (blocking) instead of clearing
                    why = cls.get("locality_reason") or f"dependency {cls['names'][:3]} not reviewed"
                    ucd.apply_update(idx[mid], "assigned", assigned_pass="deep", assigned_agent="dependency_review",
                                     clear_depends_on=cls["names"], dependency_clearance_status=cls["computed_clearance"],
                                     dependency_reason=d.get("dependency_reason") or "clear relied on an unreviewed/non-dominating downstream dependency",
                                     dependency_evidence=d.get("dependency_evidence") or [],
                                     downstream_guard_claim=True, downstream_guard_type=cls["guard_type"],
                                     guard_locality=d.get("guard_locality"),
                                     path_dominance_evidence=d.get("path_dominance_evidence"),
                                     alternative_paths_considered=d.get("alternative_paths_considered"),
                                     dependency_review_required=True,
                                     dependency_name=synth.get("dependency_name"),
                                     dependency_scope=synth.get("dependency_scope"),
                                     dependency_status=synth.get("dependency_status"),
                                     proof_status=synth.get("proof_status"),
                                     routed_reason=f"dependency-based clear blocked ({cls['status']}); {why}")
                    applied["dependency_downgraded"] += 1
                    rejected.append(f"{mid}: dependency-based clear ({cls['status']}) → routed to needs_deep_pass ({why})")
                    continue
                # non-strict (or non-blocking): record dependency metadata; flag advisory if still blocking
                dep_meta = dict(clear_depends_on=(d.get("clear_depends_on") or synth.get("clear_depends_on") or cls["names"]),
                                dependency_clearance_status=(d.get("dependency_clearance_status") or synth.get("dependency_clearance_status") or cls["computed_clearance"]),
                                dependency_reason=(d.get("dependency_reason") or synth.get("dependency_reason")),
                                dependency_evidence=(d.get("dependency_evidence") or synth.get("dependency_evidence")),
                                downstream_guard_claim=True,
                                downstream_guard_type=(d.get("downstream_guard_type") or cls["guard_type"]),
                                guard_locality=d.get("guard_locality"),
                                path_dominance_evidence=d.get("path_dominance_evidence"),
                                alternative_paths_considered=d.get("alternative_paths_considered"),
                                dependency_name=synth.get("dependency_name"),
                                dependency_scope=synth.get("dependency_scope"),
                                dependency_status=synth.get("dependency_status"),
                                proof_status=synth.get("proof_status"))
                if blocking:
                    dep_meta["dependency_review_required"] = True
                    dep_meta["routed_reason"] = f"advisory (non-strict): dependency-based clear ({cls['status']}) allowed; run validate_dependency_clears.py"
                elif decision == "advisory":
                    # P177: prose-only or incomplete/unresolvable dependency claim — recorded, NOT hard-routed.
                    dep_meta["dependency_review_required"] = True
                    dep_meta["routed_reason"] = (f"advisory: {dcu.dependency_signal_source(synth)}-only dependency "
                                                 f"signal ({cls['status']}); not hard-routed (P177 precision)")
            # math-estimator proof enforcement (additive; runs after the dependency check). A clear of a
            # math-estimator/guard/formula surface needs an independent re-derivation (math_estimator_proof),
            # not NatSpec/code agreement (QuantAMM H-11). finding-linked clears are exempt.
            me_proof = d.get("math_estimator_proof")
            man_item = man_idx.get(mid)
            me_sensitive = False
            if man_item and not d.get("finding_refs"):
                mcls = me.classify_manifest_item(man_item, taxonomy=me_tax)
                if mcls.get("math_estimator_sensitive"):
                    me_sensitive = True
                    proof_status = vme.validate_proof(me_proof, adversarial=me_adversarial)[0] if me_proof else "missing_math_proof"
                    if proof_status != "math_proof_valid" and math_strict:
                        ucd.apply_update(idx[mid], "assigned", assigned_pass="deep", assigned_agent="math_estimator_review",
                                         dependency_review_required=True,
                                         routed_reason=f"math-estimator clear blocked ({proof_status}); {mcls['math_domain']} needs an independent formula re-derivation",
                                         math_estimator_proof=me_proof)
                        applied["math_estimator_downgraded"] += 1
                        rejected.append(f"{mid}: math-estimator clear ({proof_status}, {mcls['math_domain']}) → routed to needs_deep_pass")
                        continue
                    if me_proof is not None:
                        dep_meta["math_estimator_proof"] = me_proof
            elif me_proof is not None:
                dep_meta["math_estimator_proof"] = me_proof
            # dynamic-weight lifecycle proof enforcement (P174 F1; additive; after math-estimator). A clear of
            # a dynamic-weight lifecycle surface (setWeights/update/onSwap/computeBalance) needs a
            # lifecycle-completeness proof (sum/bounds/epsilon/interval/staleness), not a thin clear (QuantAMM
            # H-04/M-04/M-08/M-09/M-12/M-14). RE-SURFACE ONLY → needs_deep_pass. finding-linked clears exempt.
            lc_proof = d.get("dynamic_weight_lifecycle_proof")
            lc_sensitive = False
            if man_item and not d.get("finding_refs"):
                lcls = dwl.classify_manifest_item(man_item, taxonomy=lc_tax)
                if lcls.get("lifecycle_sensitive"):
                    lc_sensitive = True
                    lc_status = vdwl.validate_proof(lc_proof, adversarial=lc_adversarial)[0] if lc_proof else "missing_lifecycle_proof"
                    if lc_status != "lifecycle_proof_valid" and lc_strict:
                        ucd.apply_update(idx[mid], "assigned", assigned_pass="deep",
                                         assigned_agent="dynamic_weight_lifecycle_review",
                                         dependency_review_required=True,
                                         routed_reason=(f"dynamic-weight-lifecycle clear blocked ({lc_status}); "
                                                        f"missing {', '.join(lcls.get('missing_lifecycle_checks') or []) or 'lifecycle proof'} "
                                                        f"— needs sum/bounds/epsilon/interval/staleness completeness"),
                                         dynamic_weight_lifecycle_proof=lc_proof)
                        applied["lifecycle_downgraded"] += 1
                        rejected.append(f"{mid}: dynamic-weight-lifecycle clear ({lc_status}) → routed to needs_deep_pass")
                        continue
                    if lc_proof is not None:
                        dep_meta["dynamic_weight_lifecycle_proof"] = lc_proof
            elif lc_proof is not None:
                dep_meta["dynamic_weight_lifecycle_proof"] = lc_proof
            # gate-vs-DoS adversarial check (runs before the special-focus catch-all). A clear that frames a
            # revert/underflow as an intended gate must prove the same revert can't block a legitimate actor
            # on a critical path (liquidation/withdrawal/settlement/checkpointing/force-exercise/oracle/
            # accounting/bad-debt). Missing the liveness disproof → needs_deep_pass. finding-linked exempt.
            if gd_on and not d.get("finding_refs"):
                gcls = gdu.classify(d)
                if gcls["status"] == "missing_liveness_disproof":
                    if gd_strict:
                        ucd.apply_update(idx[mid], "assigned", assigned_pass="deep",
                                         assigned_agent="gate_dos_review",
                                         routed_reason=f"{gdu.ROUTED_STATUS}: {gdu.reason(gcls)}")
                        applied["gate_dos_downgraded"] += 1
                        rejected.append(f"{mid}: intended-gate clear missing liveness disproof "
                                        f"({', '.join(gcls['missing'])}) → routed to needs_deep_pass "
                                        f"({gdu.ROUTED_STATUS})")
                        continue
                    else:
                        rejected.append(f"{mid}: [warn] intended-gate clear missing liveness disproof "
                                        f"(advisory; strict full-audit would route to needs_deep_pass)")
            # anti-false-clear spec checklists (permit / erc4626 / callback / oracle-liquidation): a clean
            # clear on a known spec-heavy surface is invalid unless the surface's checklist is completed on
            # the disposition (Revert Lend false-cleared H-01 Permit2 + M-14 ERC4626). finding-linked exempt.
            if sc_on and not d.get("finding_refs"):
                scls = scu.classify(d, man_idx.get(mid), sc_ctx)
                if scls["status"] in scu.ROUTED_STATUSES:
                    if sc_strict:
                        ucd.apply_update(idx[mid], "assigned", assigned_pass="deep",
                                         assigned_agent=f"{scls['surface']}_spec_review",
                                         routed_reason=f"{scls['status']}: {scu.reason(scls)}")
                        applied["spec_checklist_downgraded"] += 1
                        rejected.append(f"{mid}: incomplete {scls['surface']} checklist "
                                        f"({', '.join(scls['missing'])}) → routed to needs_deep_pass "
                                        f"({scu.ROUTED_STATUS})")
                        continue
                    else:
                        rejected.append(f"{mid}: [warn] incomplete {scls['surface']} spec checklist "
                                        f"(advisory; strict full-audit would route to needs_deep_pass)")
                elif sc_adversarial:
                    # fields are present — but are they CONCRETE or boilerplate? Reject confirmatory clears.
                    vcls = vscc.validate_clear(d, man_idx.get(mid), sc_ctx)
                    if vcls["status"] == vscc.CONFIRMATORY_STATUS:
                        if sc_adv_strict:
                            ucd.apply_update(idx[mid], "assigned", assigned_pass="deep",
                                             assigned_agent=f"{vcls['surface']}_spec_review",
                                             routed_reason=f"{vscc.CONFIRMATORY_STATUS}: {vscc.reason(vcls)}")
                            applied["spec_checklist_downgraded"] += 1
                            rejected.append(f"{mid}: confirmatory {vcls['surface']} checklist (boilerplate) → "
                                            f"routed to needs_deep_pass ({vscc.CONFIRMATORY_STATUS})")
                            continue
                        else:
                            rejected.append(f"{mid}: [warn] confirmatory {vcls['surface']} spec checklist "
                                            f"(advisory; strict full-audit would route to needs_deep_pass)")
            # special-focus strong-clear (CATCH-ALL, runs last): a clear on a gateway/checkpoint/subnet/
            # collateral/signature/queue/value-transfer surface may NOT be a thin local explanation. Defers
            # to the specialized validators above — only fires for special-focus items that are NOT math-
            # estimator-sensitive and NOT dependency-based clears (those carry their own deep justification).
            # Require the deep fields; conditionally require reentrancy/callback (if external calls) and
            # queue/liveness (if loops/batches/releases). Missing → needs_deep_pass (strict) / warn (advisory).
            sf_item = man_idx.get(mid)
            already_specialized = me_sensitive or lc_sensitive or dcu.is_dependency_based_clear(synth)
            sf_sig0 = (sf_item.get("signature") or "") if sf_item else ""
            # exempt read-only getters: a view/pure function has no state transition, asset movement, or
            # reentrancy to analyse — that's where thin clears are legitimate (the Recall misses were all
            # state-MUTATING functions). Keeps the bar on functions that change state.
            is_getter = bool(re.search(r"\bview\b|\bpure\b", sf_sig0)) or sf_item is not None and sf_item.get("kind") not in ("function", "constructor", "initializer")
            if (sf_on and sf_item is not None and not d.get("finding_refs") and not already_specialized
                    and not is_getter and sft.is_special_focus(sf_item, strong_threshold)):
                sig = sf_sig0 + " " + (sf_item.get("name") or "")
                sf_required = list(SF_CORE_FIELDS)
                if re.search(r"\.call\b|transfer|sendValue|safeTransfer|performCall|functionCall|\.lock\b|delegatecall", sig, re.I):
                    sf_required.append("reentrancy_callback_analysis")
                if re.search(r"batch|queue|checkpoint|release|retry|loop|pending|compact|\bfor\b|\bwhile\b", sig, re.I):
                    sf_required.append("queue_liveness_analysis")
                sf_missing = [f for f in sf_required if not (str(d.get(f) or "").strip())]
                if sf_missing:
                    if sf_strict:
                        ucd.apply_update(idx[mid], "assigned", assigned_pass="deep",
                                         assigned_agent="special_focus_review",
                                         routed_reason=(f"incomplete_strong_clear on special-focus surface "
                                                        f"({sft.special_focus_reason(sf_item, strong_threshold)}): "
                                                        f"missing {', '.join(sf_missing)} — a thin local clear is "
                                                        f"insufficient; resolve via deep pass or file a finding"))
                        applied["special_focus_downgraded"] += 1
                        rejected.append(f"{mid}: special-focus clear missing {', '.join(sf_missing)} "
                                        f"→ routed to needs_deep_pass (incomplete_strong_clear)")
                        continue
                    else:
                        rejected.append(f"{mid}: [warn] special-focus clear missing {', '.join(sf_missing)} "
                                        f"(advisory; strict full-audit would route to needs_deep_pass)")
            errs = ucd.apply_update(idx[mid], "cleared", evidence=evidence, clear_reason=reason,
                                    assigned_pass="cheap_sweep", assigned_agent="coverage_sweep",
                                    attacker_reachability=strong.get("attacker_reachability"),
                                    guard_or_invariant=strong.get("guard_or_invariant"),
                                    no_impact_reason=strong.get("no_impact_reason"), **dep_meta)
            if errs:
                rejected.append(f"{mid}: {'; '.join(errs)} (clear rejected — stays pending)"); continue
            applied["cleared"] += 1
        elif sd == "deferred_out_of_scope":
            errs = ucd.apply_update(idx[mid], "deferred_out_of_scope", scope_reason=reason,
                                    assigned_pass="cheap_sweep")
            if errs:
                rejected.append(f"{mid}: {'; '.join(errs)}"); continue
            applied["deferred_out_of_scope"] += 1
        elif sd == "needs_deep_pass":
            ucd.apply_update(idx[mid], "assigned", assigned_pass="deep",
                             assigned_agent=d.get("suggested_agent", "specialist"))
            applied["needs_deep_pass"] += 1
        elif sd == "finding":
            swp_n += 1
            fid = f"SWP-{swp_n:03d}"
            sweep_findings.append({
                "id": fid, "title": (d.get("title") or reason or "coverage-sweep finding")[:80],
                "severity": d.get("severity", "Low"), "vuln_type": d.get("vuln_type", "other"),
                "description": d.get("reason", ""), "confidence": d.get("confidence", "Low"),
                "location": {"file": d.get("file", ""), "function": d.get("name", "")},
                "impact": d.get("impact", ""), "recommendation": d.get("recommendation", "review"),
                "manifest_refs": [mid], "proof_of_concept": d.get("evidence_span", ""),
            })
            errs = ucd.apply_update(idx[mid], "finding", finding_ref=[fid],
                                    evidence=evidence, assigned_pass="cheap_sweep")
            if errs:
                rejected.append(f"{mid}: {'; '.join(errs)}"); continue
            applied["finding"] += 1

    p.write_text(json.dumps(data, indent=2))
    if sweep_findings:
        sf = audit_path("output") / "findings_coverage_sweep.json"
        existing = []
        if sf.exists():
            try:
                existing = json.loads(sf.read_text()).get("findings", [])
            except (json.JSONDecodeError, OSError):
                existing = []
        sf.write_text(json.dumps({"agent": "coverage_sweep", "contract": "sweep",
                                  "timestamp": datetime.now(timezone.utc).isoformat(),
                                  "findings": existing + sweep_findings}, indent=2))

    print(f"[ok] coverage-sweep applied: {applied}")
    if rejected:
        print(f"     [rejected {len(rejected)}] (items stay pending; gate keeps blocking):")
        for r in rejected[:15]:
            print(f"       - {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
