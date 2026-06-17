#!/usr/bin/env python3
"""
deep_pass_write.py — Validate + apply deep-pass specialist packet decisions (deterministic, no LLM).

Ingests one packet's structured decisions and resolves each needs_deep_pass item by mapping the
decision type onto an existing coverage disposition status (no new gate states, no gate weakening):

  strong_clear         -> 'cleared'  (REQUIRES evidence + attacker_reachability + guard_or_invariant
                                       + no_impact_reason; high-score strong-clear contract)
  finding              -> 'finding'  (finding_refs; if none given, mints a DPF-### finding-lead)
  PoC_needed           -> 'finding'  (mints/uses a finding-lead ref) + appends to output/poc_queue.json
  duplicate_or_known   -> 'finding'  (REQUIRES duplicate_of or known_ref as finding_ref)
  deferred_out_of_scope-> 'deferred_out_of_scope' (REQUIRES reason)

Invalid/under-evidenced decisions are REJECTED and the item stays needs_deep_pass (status 'assigned',
assigned_pass 'deep') — never silently cleared. Rejected → output/deep_pass_execution/rejected_decisions.json
(appended). Accepted summary → output/deep_pass_execution/deep_pass_write_summary.json. Finding leads →
output/deep_pass_execution/finding_leads.json (appended). PoC items → output/poc_queue.json (appended).

Usage:
    python scripts/deep_pass_write.py --decisions <packet_decisions.json>
    python scripts/deep_pass_write.py --eval --decisions <d.json> --out output/deep_pass_audit.json

--eval is the Phase-14 / Experiment E1 RESEARCH-ONLY mode: it validates the same decision schema
(plus the `likely_exploitable` mandatory-evidence fields and the REPRO_HINT presence rule) and emits a
scorer-compatible deep_pass_audit.json (candidates[] with contract/function/family/shape/confidence/
decision/repro_hint). It NEVER loads or mutates coverage_dispositions.json, mints no leads, touches no
poc_queue — it only writes the audit file the generalization scorer reads. Production wiring stays a
separate later human decision.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import update_coverage_disposition as ucd  # noqa: E402
import dependency_clear_utils as dcu  # noqa: E402
import dependency_metadata as dmeta  # noqa: E402  (P178 — structured dependency evidence capture)
import math_estimator_taxonomy as me  # noqa: E402
import validate_math_estimator_clears as vme  # noqa: E402
import gate_dos_utils as gdu  # noqa: E402
import spec_checklist_utils as scu  # noqa: E402
import validate_spec_checklist_clears as vscc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DECISION_TYPES = {"strong_clear", "finding", "PoC_needed", "duplicate_or_known", "deferred_out_of_scope"}
# Eval (research-only) accepts the same set plus likely_exploitable + needs_human. Only the finding-type
# decisions become scorer candidates (recoveries); clears/needs_human are recorded but not scored.
EVAL_FINDING_TYPES = {"finding", "likely_exploitable", "PoC_needed", "duplicate_or_known"}
EVAL_DECISION_TYPES = EVAL_FINDING_TYPES | {"strong_clear", "needs_human", "deferred_out_of_scope"}
EVAL_LIKELY_FIELDS = ("attacker_entrypoint", "divergence_point", "claimed_effect")
REPRO_HINT_FIELDS = ("state_preconditions", "required_actor", "required_assets",
                     "critical_transaction", "expected_violation")
_CONF_DEFAULT = {"finding": "high", "likely_exploitable": "medium",
                 "PoC_needed": "high", "duplicate_or_known": "medium"}


def _run_eval(dec_path: Path, out_path: Path, quiet: bool) -> int:
    """RESEARCH-ONLY: validate decisions + emit scorer-compatible deep_pass_audit.json.
    NEVER loads/mutates coverage_dispositions.json (no ucd import path touched)."""
    payload = json.loads(dec_path.read_text())
    packet_id = payload.get("packet_id", dec_path.stem)
    decisions = payload.get("decisions", payload if isinstance(payload, list) else [])
    man_idx = {}
    man_path = audit_path("output") / "coverage_manifest.json"
    if man_path.exists():
        try:
            man_idx = {i["id"]: i for i in json.loads(man_path.read_text()).get("items", [])}
        except (json.JSONDecodeError, OSError):
            man_idx = {}

    candidates, rejected = [], []
    counts = {"finding": 0, "likely_exploitable": 0, "strong_clear": 0,
              "needs_human": 0, "deferred_out_of_scope": 0, "with_repro_hint": 0}
    for d in decisions:
        dt = d.get("decision")
        mid = d.get("manifest_id")
        if dt not in EVAL_DECISION_TYPES:
            rejected.append({**d, "_reject": f"invalid decision '{dt}'"}); continue
        item = man_idx.get(mid, {})
        if dt not in EVAL_FINDING_TYPES:
            counts[dt] = counts.get(dt, 0) + 1
            continue
        ev = d.get("evidence_span") or d.get("evidence")
        if not ev:
            rejected.append({**d, "_reject": "finding-type missing evidence_span"}); continue
        if dt == "likely_exploitable":
            miss = [f for f in EVAL_LIKELY_FIELDS if not (str(d.get(f) or "")).strip()]
            if miss:
                rejected.append({**d, "_reject": f"likely_exploitable missing mandatory evidence {miss}"})
                continue
        # REPRO_HINT mandatory for finding + likely_exploitable (keys present; values may be "unknown")
        if dt in ("finding", "likely_exploitable"):
            rh = d.get("repro_hint")
            if not isinstance(rh, dict) or [f for f in REPRO_HINT_FIELDS if f not in rh]:
                rejected.append({**d, "_reject": f"missing/incomplete repro_hint (need {list(REPRO_HINT_FIELDS)})"})
                continue
            counts["with_repro_hint"] += 1
        contract = d.get("contract") or item.get("contract") or ""
        function = d.get("function") or item.get("name") or ""
        if not function:
            rejected.append({**d, "_reject": "no function (decision/manifest)"}); continue
        conf = d.get("confidence") or _CONF_DEFAULT.get(dt, "medium")
        if conf not in ("high", "medium", "low"):
            conf = _CONF_DEFAULT.get(dt, "medium")
        counts[dt] = counts.get(dt, 0) + 1
        candidates.append({
            "manifest_id": mid, "contract": contract, "function": function,
            "family": d.get("family", "value_flow_parity"), "shape": d.get("shape", ""),
            "confidence": conf, "decision": dt,
            "evidence_span": ev if isinstance(ev, str) else (ev[0] if ev else ""),
            "divergence_point": d.get("divergence_point"),
            "repro_hint": d.get("repro_hint"),
            "lens_id": f"deep_pass:{contract}.{function}:{d.get('shape','')}",
        })

    by_conf = {c: sum(1 for x in candidates if x["confidence"] == c) for c in ("high", "medium", "low")}
    report = {
        "lens": "deep_pass", "generated_at": datetime.now(timezone.utc).isoformat(),
        "packet_id": packet_id, "manifest": str(man_path),
        "is_gate": False, "research_only": True, "routes_in_production": False,
        "routed_manifest_ids": [], "eval_mode": True,
        "raw_candidates": len(candidates), "by_confidence": by_conf,
        "high": by_conf["high"], "medium": by_conf["medium"], "low": by_conf["low"],
        "decision_counts": counts, "rejected": len(rejected),
        "candidates": candidates,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))
    if rejected:
        (out_path.parent / "deep_pass_eval_rejected.json").write_text(
            json.dumps({"packet_id": packet_id, "rejected": rejected}, indent=2))
    if not quiet:
        print(f"[ok] deep_pass_write --eval [{packet_id}]: RESEARCH-ONLY (dispositions untouched) · "
              f"candidates {len(candidates)} (high {by_conf['high']} medium {by_conf['medium']}) · "
              f"repro_hints {counts['with_repro_hint']} · rejected {len(rejected)} · wrote {out_path}")
        for r in rejected[:8]:
            print(f"     REJECT {r.get('manifest_id')}: {r['_reject']}")
    return 0


def _append_json_list(path: Path, items: list, key: str):
    existing = []
    if path.exists():
        try:
            existing = json.loads(path.read_text()).get(key, [])
        except (json.JSONDecodeError, OSError):
            existing = []
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({key: existing + items}, indent=2))
    return len(existing) + len(items)


def _next_lead_id(leads_path: Path) -> int:
    if not leads_path.exists():
        return 1
    try:
        return len(json.loads(leads_path.read_text()).get("leads", [])) + 1
    except (json.JSONDecodeError, OSError):
        return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--eval", action="store_true",
                    help="RESEARCH-ONLY: emit scorer-compatible deep_pass_audit.json; never touch dispositions")
    ap.add_argument("--out", default="output/deep_pass_audit.json",
                    help="(--eval) output audit path, relative to active audit root")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    dec_path = Path(args.decisions)
    if not dec_path.exists():
        raise SystemExit(f"[deep_pass_write] decisions not found: {dec_path}")

    if args.eval:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            # resolve relative to the active audit root (e.g. "output/deep_pass_audit.json")
            parts = out_path.parts
            out_path = audit_path(parts[0], *parts[1:]) if len(parts) > 1 else audit_path(str(out_path))
        return _run_eval(dec_path, out_path, args.quiet)

    payload = json.loads(dec_path.read_text())
    packet_id = payload.get("packet_id", dec_path.stem)
    decisions = payload.get("decisions", payload if isinstance(payload, list) else [])

    p, data, idx = ucd._load()  # dispositions
    pol = {}
    try:
        pol = json.loads((ROOT / "config" / "agent_policy.json").read_text()).get("coverage_policy", {})
    except Exception:
        pass
    strong_fields = pol.get("strong_clear_fields", ["attacker_reachability", "guard_or_invariant", "no_impact_reason"])
    # dependency-aware clear policy
    dep_require = pol.get("require_dependency_clear_metadata", True)
    full_audit = os.environ.get("AUDITWATCH_FULL_AUDIT", "").strip().lower() in ("1", "true", "yes", "on")
    dep_strict = pol.get("dependency_clear_strict", False) or (pol.get("dependency_clear_strict_full_audit", True) and full_audit)
    locality_on = pol.get("dependency_locality_strict", False) or (pol.get("dependency_locality_strict_full_audit", True) and full_audit)
    dep_blocking_statuses = dcu.BLOCKING_CLASSIFICATIONS | (dcu.LOCALITY_BLOCKING if locality_on else set())
    # P177: prose-only / incomplete dependency claims are advisory; hard-route only on complete structured
    # metadata resolving an in-scope unproven guard. Reversible via guarded_downstream_require_structured.
    dep_require_structured = pol.get("guarded_downstream_require_structured", True)
    manifest_items = []
    man_path = audit_path("output") / "coverage_manifest.json"
    if man_path.exists():
        try:
            manifest_items = json.loads(man_path.read_text()).get("items", [])
        except (json.JSONDecodeError, OSError):
            manifest_items = []
    name_index = dcu.build_manifest_name_index(manifest_items)
    cg_path = audit_path("data") / "interactions" / "call_graph.json"
    call_graph = {}
    if cg_path.exists():
        try:
            call_graph = json.loads(cg_path.read_text())
        except (json.JSONDecodeError, OSError):
            call_graph = {}
    # math-estimator proof policy (additive; layered after the dependency check).
    man_idx = {i["id"]: i for i in manifest_items}
    me_tax = me.load_taxonomy()
    me_require = pol.get("require_math_estimator_proof", True)
    math_strict = me_require and (pol.get("math_estimator_strict", False)
                                  or (pol.get("math_estimator_strict_full_audit", True) and full_audit))
    gd_strict = pol.get("gate_vs_dos_enabled", True) and (
        pol.get("gate_vs_dos_strict", False)
        or (pol.get("gate_vs_dos_strict_full_audit", True) and full_audit))
    sc_strict = pol.get("spec_checklist_enabled", True) and (
        pol.get("spec_checklist_strict", False)
        or (pol.get("spec_checklist_strict_full_audit", True) and full_audit))
    # adversarial: a field-complete strong_clear of boilerplate is rejected as confirmatory (Hybra reward fns).
    sc_adversarial = pol.get("spec_checklist_enabled", True) and pol.get("spec_checklist_adversarial", True)
    sc_adv_strict = sc_adversarial and (pol.get("spec_checklist_adversarial_strict", False)
                                        or (pol.get("spec_checklist_adversarial_strict_full_audit", True) and full_audit))
    sc_ctx = scu.build_context(man_idx.values())  # run-level reward-layer / external-market signals
    me_adversarial = pol.get("math_adversarial_proof", True)

    exec_dir = audit_path("output") / "deep_pass_execution"
    leads_path = exec_dir / "finding_leads.json"
    poc_path = audit_path("output") / "poc_queue.json"

    applied = {k: 0 for k in DECISION_TYPES}
    applied["math_estimator_downgraded"] = 0
    applied["gate_dos_downgraded"] = 0
    applied["spec_checklist_downgraded"] = 0
    rejected = []
    new_leads = []
    new_poc = []
    lead_n = _next_lead_id(leads_path)

    for d in decisions:
        mid = d.get("manifest_id")
        dt = d.get("decision")
        if mid not in idx:
            rejected.append({**d, "_reject": "unknown manifest_id"}); continue
        if dt not in DECISION_TYPES:
            rejected.append({**d, "_reject": f"invalid decision '{dt}'"}); continue
        evidence = d.get("evidence") or ([d["evidence_span"]] if d.get("evidence_span") else [])
        reason = d.get("reasoning_summary") or d.get("reason")
        if not evidence:
            rejected.append({**d, "_reject": "missing evidence/evidence_span"}); continue

        if dt == "strong_clear":
            missing = [f for f in strong_fields if not (d.get(f) or "").strip()]
            if missing:
                rejected.append({**d, "_reject": f"strong_clear missing {missing}"}); continue
            # dependency-aware enforcement: a strong_clear may not lean on an unreviewed dependency.
            synth = {"status": "cleared", "manifest_id": mid, "clear_reason": reason,
                     "guard_or_invariant": d.get("guard_or_invariant"), "no_impact_reason": d.get("no_impact_reason"),
                     "clear_depends_on": d.get("clear_depends_on"),
                     "dependency_clearance_status": d.get("dependency_clearance_status"),
                     "dependency_reason": d.get("dependency_reason"), "dependency_evidence": d.get("dependency_evidence"),
                     "downstream_guard_claim": d.get("downstream_guard_claim"), "downstream_guard_type": d.get("downstream_guard_type"),
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
                # P178: auto-capture resolved structured dependency facts (fail-open; resolve-or-nothing →
                # unresolved prose stays advisory). Feeds the UNCHANGED P177 router; no routing-rule change.
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
                    why = cls.get("locality_reason") or f"dependency {cls['names'][:3]} not reviewed"
                    ucd.apply_update(idx[mid], "assigned", assigned_pass="deep", assigned_agent="dependency_review",
                                     clear_depends_on=cls["names"], dependency_clearance_status=cls["computed_clearance"],
                                     dependency_reason=d.get("dependency_reason") or "strong_clear relied on an unreviewed/non-dominating downstream dependency",
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
                                     routed_reason=f"dependency-based strong_clear blocked ({cls['status']}); {why}")
                    rejected.append({**d, "_reject": f"dependency-based strong_clear ({cls['status']}) → routed to needs_deep_pass ({why})"})
                    continue
                dep_meta = dict(clear_depends_on=(d.get("clear_depends_on") or synth.get("clear_depends_on") or cls["names"]),
                                dependency_clearance_status=(d.get("dependency_clearance_status") or synth.get("dependency_clearance_status") or cls["computed_clearance"]),
                                dependency_reason=(d.get("dependency_reason") or synth.get("dependency_reason")),
                                dependency_evidence=(d.get("dependency_evidence") or synth.get("dependency_evidence")),
                                downstream_guard_claim=True, downstream_guard_type=(d.get("downstream_guard_type") or cls["guard_type"]),
                                guard_locality=d.get("guard_locality"),
                                path_dominance_evidence=d.get("path_dominance_evidence"),
                                alternative_paths_considered=d.get("alternative_paths_considered"),
                                dependency_name=synth.get("dependency_name"),
                                dependency_scope=synth.get("dependency_scope"),
                                dependency_status=synth.get("dependency_status"),
                                proof_status=synth.get("proof_status"))
                if blocking:
                    dep_meta["dependency_review_required"] = True
                    dep_meta["routed_reason"] = f"advisory (non-strict): dependency-based strong_clear ({cls['status']}) allowed"
                elif decision == "advisory":
                    # P177: prose-only or incomplete/unresolvable dependency claim — recorded, NOT hard-routed.
                    dep_meta["dependency_review_required"] = True
                    dep_meta["routed_reason"] = (f"advisory: {dcu.dependency_signal_source(synth)}-only dependency "
                                                 f"signal ({cls['status']}); not hard-routed (P177 precision)")
            # math-estimator proof enforcement (additive; after the dependency check). A strong_clear of a
            # math-estimator/guard/formula surface needs an independent re-derivation (math_estimator_proof),
            # not NatSpec/code agreement (QuantAMM H-11). finding-linked strong_clears are exempt.
            me_proof = d.get("math_estimator_proof")
            man_item = man_idx.get(mid)
            if man_item and not d.get("finding_refs"):
                mcls = me.classify_manifest_item(man_item, taxonomy=me_tax)
                if mcls.get("math_estimator_sensitive"):
                    proof_status = vme.validate_proof(me_proof, adversarial=me_adversarial)[0] if me_proof else "missing_math_proof"
                    if proof_status != "math_proof_valid" and math_strict:
                        ucd.apply_update(idx[mid], "assigned", assigned_pass="deep", assigned_agent="math_estimator_review",
                                         dependency_review_required=True,
                                         routed_reason=f"math-estimator strong_clear blocked ({proof_status}); {mcls['math_domain']} needs an independent formula re-derivation",
                                         math_estimator_proof=me_proof)
                        applied["math_estimator_downgraded"] += 1
                        rejected.append({**d, "_reject": f"math-estimator strong_clear ({proof_status}, {mcls['math_domain']}) → routed to needs_deep_pass"})
                        continue
                    if me_proof is not None:
                        dep_meta["math_estimator_proof"] = me_proof
            elif me_proof is not None:
                dep_meta["math_estimator_proof"] = me_proof
            # gate-vs-DoS: an "intended revert/underflow" strong_clear needs a liveness disproof.
            if gd_strict and not d.get("finding_refs"):
                gcls = gdu.classify(d)
                if gcls["status"] == "missing_liveness_disproof":
                    ucd.apply_update(idx[mid], "assigned", assigned_pass="deep", assigned_agent="gate_dos_review",
                                     routed_reason=f"{gdu.ROUTED_STATUS}: {gdu.reason(gcls)}")
                    applied["gate_dos_downgraded"] += 1
                    rejected.append({**d, "_reject": f"intended-gate strong_clear missing liveness disproof "
                                                     f"({', '.join(gcls['missing'])}) → needs_deep_pass"})
                    continue
            # anti-false-clear spec checklist: a clean strong_clear on a permit/erc4626/callback/oracle
            # surface needs the surface's checklist completed (Revert Lend H-01/M-14 false clears).
            if sc_strict and not d.get("finding_refs"):
                scls = scu.classify(d, man_idx.get(mid), sc_ctx)
                if scls["status"] in scu.ROUTED_STATUSES:
                    ucd.apply_update(idx[mid], "assigned", assigned_pass="deep",
                                     assigned_agent=f"{scls['surface']}_spec_review",
                                     routed_reason=f"{scls['status']}: {scu.reason(scls)}")
                    applied["spec_checklist_downgraded"] += 1
                    rejected.append({**d, "_reject": f"incomplete {scls['surface']} checklist "
                                                     f"({', '.join(scls['missing'])}) → needs_deep_pass"})
                    continue
            if sc_adv_strict and not d.get("finding_refs"):
                vcls = vscc.validate_clear(d, man_idx.get(mid), sc_ctx)
                if vcls["status"] == vscc.CONFIRMATORY_STATUS:
                    ucd.apply_update(idx[mid], "assigned", assigned_pass="deep",
                                     assigned_agent=f"{vcls['surface']}_spec_review",
                                     routed_reason=f"{vscc.CONFIRMATORY_STATUS}: {vscc.reason(vcls)}")
                    applied["spec_checklist_downgraded"] += 1
                    rejected.append({**d, "_reject": f"confirmatory {vcls['surface']} checklist (boilerplate) → needs_deep_pass"})
                    continue
            errs = ucd.apply_update(idx[mid], "cleared", evidence=evidence, clear_reason=reason,
                                    assigned_pass="deep", assigned_agent=d.get("specialist", "deep_pass"),
                                    attacker_reachability=d.get("attacker_reachability"),
                                    guard_or_invariant=d.get("guard_or_invariant"),
                                    no_impact_reason=d.get("no_impact_reason"), **dep_meta)
            if errs:
                rejected.append({**d, "_reject": "; ".join(errs)}); continue
            applied["strong_clear"] += 1

        elif dt in ("finding", "PoC_needed", "duplicate_or_known"):
            refs = list(d.get("finding_refs") or [])
            if dt == "duplicate_or_known":
                ref = d.get("duplicate_of") or d.get("known_ref")
                if not ref:
                    rejected.append({**d, "_reject": "duplicate_or_known needs duplicate_of/known_ref"}); continue
                refs = [ref] + refs
            if not refs:
                lead = f"DPF-{lead_n:03d}"; lead_n += 1
                new_leads.append({"lead_id": lead, "manifest_id": mid, "packet": packet_id,
                                  "title": d.get("title", reason or "deep-pass lead"),
                                  "file": d.get("file", ""), "name": d.get("name", ""),
                                  "severity_ceiling": d.get("severity_ceiling", ""),
                                  "decision": dt, "reasoning": reason,
                                  "attacker_entrypoint": d.get("attacker_entrypoint"),
                                  "preconditions": d.get("preconditions"),
                                  "state_transition": {"before": d.get("state_before"),
                                                       "transition": d.get("state_transition"),
                                                       "after": d.get("state_after")},
                                  "impact_category": d.get("impact_category"),
                                  "why_guards_fail": d.get("why_guards_fail"),
                                  "confidence": d.get("confidence")})
                refs = [lead]
            errs = ucd.apply_update(idx[mid], "finding", finding_ref=refs, evidence=evidence,
                                    assigned_pass="deep", assigned_agent=d.get("specialist", "deep_pass"))
            if errs:
                rejected.append({**d, "_reject": "; ".join(errs)}); continue
            if dt == "PoC_needed":
                new_poc.append({"manifest_id": mid, "finding_refs": refs, "packet": packet_id,
                                "file": d.get("file", ""), "name": d.get("name", ""),
                                "poc_plan": d.get("min_poc_plan") or d.get("poc_plan", ""),
                                "severity_ceiling": d.get("severity_ceiling", ""),
                                "attacker_entrypoint": d.get("attacker_entrypoint")})
            applied[dt] += 1

        elif dt == "deferred_out_of_scope":
            if not reason:
                rejected.append({**d, "_reject": "deferred needs reason"}); continue
            errs = ucd.apply_update(idx[mid], "deferred_out_of_scope", scope_reason=reason, assigned_pass="deep")
            if errs:
                rejected.append({**d, "_reject": "; ".join(errs)}); continue
            applied["deferred_out_of_scope"] += 1

    p.write_text(json.dumps(data, indent=2))
    if new_leads:
        _append_json_list(leads_path, new_leads, "leads")
    if new_poc:
        _append_json_list(poc_path, new_poc, "poc_queue")
    if rejected:
        _append_json_list(exec_dir / "rejected_decisions.json",
                          [{**r, "packet": packet_id} for r in rejected], "rejected")
    # per-run summary (overwrite with this packet's result)
    (exec_dir / "deep_pass_write_summary.json").parent.mkdir(parents=True, exist_ok=True)
    (exec_dir / "deep_pass_write_summary.json").write_text(json.dumps({
        "packet_id": packet_id, "generated_at": datetime.now(timezone.utc).isoformat(),
        "decisions_in": len(decisions), "applied": applied,
        "rejected": len(rejected), "new_finding_leads": len(new_leads), "new_poc_items": len(new_poc),
    }, indent=2))

    print(f"[ok] deep_pass_write [{packet_id}]: applied={applied} rejected={len(rejected)} "
          f"leads={len(new_leads)} poc={len(new_poc)}")
    for r in rejected[:8]:
        print(f"     REJECT {r.get('manifest_id')}: {r['_reject']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
