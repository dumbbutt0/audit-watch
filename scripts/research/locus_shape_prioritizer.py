#!/usr/bin/env python3
"""
locus_shape_prioritizer.py — P260 RESEARCH-ONLY, DEFAULT-OFF, UN-WIRED locus-prioritization + shape-discovery module.

Motivation (P259): the binding gap is LOCUS_SELECTION. The shape vocabulary (8 templates) is adequate and B/C
ranking helps once the right mechanism surfaces, but the procedure skips award-carrying loci (e.g. a checkpoint
already HIT hybra GrowthHYBR.deposit but locus-selection skipped it). This module is the missing upstream step:
it takes existing frozen artifacts (coverage manifest + accounting/state-transition checkpoint outputs + optional
base candidates), PRIORITIZES the highest-risk loci (preferring skipped high-risk checkpoint-hit loci over
already-completed base candidates), APPLIES the 8 shape templates, and EMITS top-2 mechanism hypotheses + B/C
ranking handoff for downstream ranking / five-operation completion.

HARD INVARIANTS (self-tripwire, mirrors the checkpoint architecture):
  - is_gate:false · research_only:true · routes_in_production:false · routed_manifest_ids:[]
  - emits_findings:false · concludes_vulnerability:false
  - NEVER sets severity / confidence / verdict / reportability. Output is interrogative hypotheses only.
  - Requires NO answer key. Reads manifest + checkpoint JSON (+ optional base candidates) only.

Usage:
  python scripts/research/locus_shape_prioritizer.py --manifest <p> --accounting <p> --state-transition <p> \
      [--base-candidates <p>] [--with-source] --out <out.json> [--top-n N] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT / "config" / "research_locus_shape_prioritizer.json"
_BODY_MAX_LINES = 400


def _load_json(path: str | Path) -> dict | list:
    try:
        return json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _checkpoint_hits(report: dict) -> dict:
    """contract:function -> set of families fired (accounting_family|state_family)."""
    hits: dict[str, set] = defaultdict(set)
    for rec in (report or {}).get("records", []):
        key = f"{rec.get('contract','')}:{rec.get('function','')}"
        fam = rec.get("accounting_family") or rec.get("state_family")
        if fam:
            hits[key].add(fam)
    return hits


def _base_tags(base: dict | list) -> dict:
    """Optional base-candidate map: 'contract:function' or function-name -> tag (BASE_COMPLETED/BASE_BORN_INCOMPLETE)."""
    out: dict[str, str] = {}
    items = base.get("candidates", base) if isinstance(base, dict) else base
    if isinstance(items, list):
        for c in items:
            if not isinstance(c, dict):
                continue
            key = c.get("locus") or f"{c.get('contract','')}:{c.get('function','')}"
            tag = (c.get("tag") or c.get("three_way_tag") or "").upper()
            if key and tag:
                out[key] = tag
    return out


def _function_body(file_rel: str, start: int, cache: dict) -> str:
    if not file_rel or not start:
        return ""
    if file_rel not in cache:
        try:
            cache[file_rel] = (ROOT / file_rel).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            cache[file_rel] = []
    lines = cache[file_rel]
    if not lines:
        return ""
    i = max(0, (start or 1) - 1)
    n = len(lines)
    j = i
    while j < min(n, i + 25) and "{" not in lines[j]:
        j += 1
    if j >= min(n, i + 25) or "{" not in lines[j]:
        return ""
    depth, out, started = 0, [], False
    for k in range(j, min(n, j + _BODY_MAX_LINES)):
        line = lines[k]
        out.append(line)
        depth += line.count("{") - line.count("}")
        if "{" in line:
            started = True
        if started and depth <= 0:
            break
    return "\n".join(out)[:12000]


def _name_buckets(name_l: str, sig_l: str, tags: list, cfg: dict) -> set:
    """Which keyword-dimension buckets this locus matches."""
    blob = name_l + " " + sig_l + " " + " ".join(t.lower() for t in (tags or []))
    matched = set()
    for dim, kws in cfg["keyword_dimensions"].items():
        if any(kw in blob for kw in kws):
            matched.add(dim)
    return matched


def _route_templates(name_l: str, sig_l: str, has_ext_call: bool, body_l: str, cfg: dict) -> list:
    """Map signals -> applicable shape templates T1-T8."""
    blob = name_l + " " + sig_l + " " + body_l
    applied = []
    for tmpl, markers in cfg["marker_templates"].items():
        hit = False
        for m in markers:
            if m == "external_call":
                if has_ext_call:
                    hit = True
                    break
            elif m in blob:
                hit = True
                break
        if hit:
            applied.append(tmpl)
    return applied


# Static interrogative scaffolds per template (no conclusions; downstream operator/LLM answers them).
_TEMPLATE_SPEC = {
    "T1_external_dependency_availability": (
        "An external liquidity/state/price/allowance condition may block a required protocol action here.",
        "Can an external protocol (AMM/lending/oracle) be driven to a state that makes this action revert or mis-execute?"),
    "T2_redemption_withdrawal_state_coupling": (
        "A withdraw/redeem/burn/settle/claim path may alter accounting state affecting later solvency/fees/shares/debt.",
        "Does this path mutate shared accounting that a later operation relies on for correctness?"),
    "T3_reentrancy_accounting_boundary": (
        "An external call/transfer/callback may occur before accounting/index/share/debt state is finalized.",
        "Is there a call/transfer to an arbitrary party before all relevant state is written?"),
    "T4_migration_conversion_residue": (
        "Value/rewards/shares/debt/indexes/permissions may be lost, duplicated, or mispriced across old/new domains.",
        "Across this conversion/migration/split/merge, is every unit and right conserved exactly?"),
    "T5_statemachine_liveness_terminality": (
        "A state transition may make a required later operation impossible, stuck, delayed, or incorrectly successful.",
        "After this transition, can a needed later step (claim/finalize/withdraw) still complete correctly?"),
    "T6_cross_transaction_drift": (
        "Separate txs/epochs/delayed checkpoints may create a stale or double-counted accounting view.",
        "Across two transactions/epochs, can an index/accrual be applied twice or skipped?"),
    "T7_liquidation_solvency_boundary": (
        "A user/liquidator may manipulate the solvent/insolvent / repay-vs-collateral / eligibility / bad-debt boundary.",
        "Can the actor choose inputs/timing to seize more than fair, or push a position across the solvency line?"),
    "T8_shareprice_donation_inflation": (
        "External value movement or supply manipulation may alter share price / exchange rate / proportional claims.",
        "Can a first-depositor / donation / rounding-to-zero condition skew the share price or claims?"),
}


def _mk_mechanism(tmpl: str, contract: str, fn: str, signature: str, markers: list) -> dict:
    summary, falsifier = _TEMPLATE_SPEC[tmpl]
    return {
        "template_id": tmpl,
        "mechanism_summary": f"[{tmpl.split('_')[0]}] {contract}.{fn}: {summary}",
        "source_backed_trigger": f"{contract}.{fn} {signature}".strip(),
        "matched_markers": markers,
        "attacker_action": "operator-to-derive (who calls it, with what input/timing/state)",
        "affected_state_assets_permissions": "operator-to-derive (which shares/debt/reward/collateral/permission)",
        "expected_value_delta": "operator-to-derive",
        "victim_gainer_hypothesis": "operator-to-derive",
        "terminality_hypothesis": "operator-to-derive (persists? strands? extractable?)",
        "amplification_hypothesis": "operator-to-derive (repeat/lever/flash-loan/scale?)",
        "protocol_comparand_hint": "operator-to-derive (sibling fn / invariant / comment / reference)",
        "assumptions": "operator-to-derive",
        "falsification_question": falsifier,
        "ranking_features_for_profile_B": {  # messy-reconciliation weighted
            "reconciliation_or_solvency_or_convexity_or_drift": tmpl in (
                "T1_external_dependency_availability", "T4_migration_conversion_residue",
                "T6_cross_transaction_drift", "T7_liquidation_solvency_boundary",
                "T8_shareprice_donation_inflation"),
            "messy_not_tidy": True,
        },
        "ranking_features_for_profile_C": {  # runner-up challenge
            "candidate_for_runner_up_overtake": True,
            "terminal_delta_class": tmpl,
        },
        # invariants (never concluded)
        "output_type": "mechanism_hypothesis",
        "concluded": False,
        "severity": None,
        "confidence": None,
    }


def prioritize(manifest: dict, acct: dict, st: dict, base: dict | list, cfg: dict,
               with_source: bool) -> list:
    items = manifest.get("items", []) if isinstance(manifest, dict) else []
    fn_items = [it for it in items
                if it.get("kind") in ("function", "initializer", "constructor")
                and it.get("in_scope", True)]
    acct_hits, st_hits = _checkpoint_hits(acct), _checkpoint_hits(st)
    base_map = _base_tags(base) if base else {}
    w = cfg["weights"]
    src_cache: dict = {}
    loci = []
    for it in fn_items:
        contract, fn = it.get("contract", ""), it.get("name", "")
        key = f"{contract}:{fn}"
        name_l, sig_l = fn.lower(), (it.get("signature", "") or "").lower()
        fams = acct_hits.get(key, set()) | st_hits.get(key, set())
        cp_strength = len(fams)
        if cp_strength == 0 and (it.get("attack_surface_score", 0) or 0) < 3:
            continue  # skip low-signal, non-checkpoint loci to bound output
        buckets = _name_buckets(name_l, sig_l, it.get("tags", []), cfg)
        has_ext = bool(it.get("external_calls"))
        body_l = ""
        if with_source:
            span = it.get("source_span", {}) or {}
            body_l = _function_body(it.get("file", ""), span.get("start_line"), src_cache).lower()

        dims = {
            "checkpoint_hit_strength": float(cp_strength),
            "accounting_state_surface_density": float(len(acct_hits.get(key, set())) > 0)
                                                + float(len(st_hits.get(key, set())) > 0),
            "asset_share_debt_reward_vars": float(any(k in (name_l + sig_l) for k in
                ("share", "asset", "debt", "reward", "collateral", "lock", "balance", "amount"))),
            "lifecycle_criticality": float("lifecycle_criticality" in buckets),
            "external_call_callback": float(has_ext),
            "cross_contract_identity": float(any(k in (name_l + sig_l) for k in
                ("onbehalf", "receiver", "recipient", "to", "from", "owner", "liquidator", "beneficiary"))),
            "first_depositor_donation_shareprice": float("first_depositor_donation_shareprice" in buckets),
            "liquidation_solvency": float("liquidation_solvency" in buckets),
            "redemption_withdrawal_migration": float("redemption_withdrawal_migration" in buckets),
            "queue_auction_statemachine": float("queue_auction_statemachine" in buckets),
            "base_candidate_incompleteness": float(base_map.get(key, "") == "BASE_BORN_INCOMPLETE"),
            "downstream_exploitability": float(bool(it.get("in_tainted_sink")) or bool(it.get("has_loop"))),
            "attack_surface_score": float(it.get("attack_surface_score", 0) or 0),
            "risk_score": float(it.get("risk_score", 0) or 0),
        }
        score = sum(w.get(k, 0.0) * v for k, v in dims.items())
        # P259 rule: prefer skipped high-risk checkpoint-hit loci over already-completed base candidates.
        if base_map.get(key, "") == "BASE_COMPLETED_CHAIN":
            score += cfg["base_completed_penalty"]
        templates = _route_templates(name_l, sig_l, has_ext, body_l, cfg)
        if not templates:
            continue
        mechs = [_mk_mechanism(t, contract, fn, it.get("signature", ""), templates) for t in templates]
        # top-2 mechanisms = the two templates most aligned with this locus's dominant risk buckets
        prio_order = ["T7_liquidation_solvency_boundary", "T8_shareprice_donation_inflation",
                      "T4_migration_conversion_residue", "T1_external_dependency_availability",
                      "T2_redemption_withdrawal_state_coupling", "T6_cross_transaction_drift",
                      "T5_statemachine_liveness_terminality", "T3_reentrancy_accounting_boundary"]
        ranked = sorted(mechs, key=lambda m: prio_order.index(m["template_id"]) if m["template_id"] in prio_order else 99)
        top2 = ranked[:2]
        action = ("APPLY_RANKING" if cp_strength >= 1 and score >= cfg["min_priority_score"]
                  else "NEEDS_MANUAL_REVIEW" if score >= cfg["min_priority_score"]
                  else "LOW_PRIORITY")
        if templates and any(t in ("T3_reentrancy_accounting_boundary",) for t in templates) and has_ext:
            action = "REFUTE_FIRST"
        loci.append({
            "locus_id": it.get("id"),
            "contract": contract,
            "function": fn,
            "source_path": it.get("file"),
            "source_span": it.get("source_span"),
            "base_signal": base_map.get(key, "none"),
            "checkpoint_signal": sorted(fams),
            "why_prioritized": (f"checkpoint families={sorted(fams)}; buckets={sorted(buckets)}; "
                                f"ext_call={has_ext}; attack_surface={it.get('attack_surface_score')}"),
            "locus_priority_score": round(score, 3),
            "priority_dimensions": {k: round(v, 2) for k, v in dims.items() if v},
            "applied_shape_templates": templates,
            "generated_mechanism_hypotheses": mechs,
            "top_2_mechanisms": [m["template_id"] for m in top2],
            "bc_ranking_handoff": {
                "profile_B_inputs": [m["ranking_features_for_profile_B"] for m in top2],
                "profile_C_inputs": [m["ranking_features_for_profile_C"] for m in top2],
                "note": "module does NOT decide severity/reportability; feeds Profile B/C ranking + five-operation completion",
            },
            "falsification_questions": [m["falsification_question"] for m in top2],
            "downstream_recommended_action": action,
        })
    loci.sort(key=lambda x: x["locus_priority_score"], reverse=True)
    return loci


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--accounting", required=True)
    ap.add_argument("--state-transition", required=True)
    ap.add_argument("--base-candidates")
    ap.add_argument("--with-source", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--top-n", type=int)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    cfg = _load_json(CONFIG_PATH)
    if not cfg:
        raise SystemExit(f"[locus_shape_prioritizer] missing config {CONFIG_PATH}")
    top_n = args.top_n or cfg.get("top_n", 15)
    manifest = _load_json(args.manifest)
    acct = _load_json(args.accounting)
    st = _load_json(args.state_transition)
    base = _load_json(args.base_candidates) if args.base_candidates else None

    loci = prioritize(manifest, acct, st, base, cfg, args.with_source)
    bounded = loci[:top_n]

    # Self-tripwire: this module must never conclude.
    for lc in bounded:
        for m in lc["generated_mechanism_hypotheses"]:
            assert m.get("severity") is None and m.get("concluded") is False, \
                "INVARIANT VIOLATION: prioritizer emitted a conclusion — it must only emit interrogative hypotheses"

    report = {
        "module": "locus_shape_prioritizer",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(args.manifest),
        "is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": [],
        "emits_findings": False, "concludes_vulnerability": False,
        "output_type": "locus_priority_hypotheses",
        "top_n": top_n,
        "total_candidate_loci": len(loci),
        "prioritized_loci": bounded,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    if not args.quiet:
        print(f"[locus_shape_prioritizer] research-only/default-off · candidate-loci {len(loci)} · "
              f"emitted top-{len(bounded)} · wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
