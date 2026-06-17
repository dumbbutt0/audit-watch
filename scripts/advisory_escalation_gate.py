#!/usr/bin/env python3
"""
advisory_escalation_gate.py — route HIGH-RISK advisory-lens hits to needs_deep_pass instead of leaving them
advisory-only. Closes the standing "advisory lens hit → routing_gap" (Recall: recipient lens hit AssetHelper
→H-09, cross-artifact lens hit newSubnetActor→H-08, both ignored because advisory).

It reads the advisory lens outputs (cross_artifact_lifecycle, recipient_custody, griefing_dos,
cross_function_invariant, asset_source_consistency, checkpoint_liveness). For any HIGH-RISK hit whose
manifest surface matches the high-risk escalation term set AND whose CURRENT disposition is `cleared`, it
re-routes that item to needs_deep_pass (disposition `assigned`, assigned_pass=deep). It NEVER converts a hit
to a finding, and NEVER touches non-high-risk hits or items not currently cleared.

Strict full-audit only: active when advisory_escalation_strict OR (advisory_escalation_strict_full_audit AND
AUDITWATCH_FULL_AUDIT=1). Override AUDITWATCH_ADVISORY_ESCALATION_OVERRIDE=1 → report but do not re-route.
Exit 0 always (re-routing makes the coverage completeness gate block until a deep pass resolves the item).

Writes output/advisory_escalation_gate.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import update_coverage_disposition as ucd  # noqa: E402
import special_focus_terms as sft  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Which specialist should resolve a deep pass routed by each advisory lens. The deep-pass queue
# derives cluster priority + suggested specialist from assigned_agent, so carrying the right
# specialist here is what makes the routed item land on the correct reviewer.
LENS_SPECIALIST = {
    "recipient_custody": "access_control",
    "cross_function_invariant": "logic",
    "asset_source_consistency": "logic",
    "checkpoint_liveness": "dos",
    "cross_artifact_lifecycle": "logic",
    "griefing_dos": "dos",
    "abi_getter_mismatch": "logic",
    "arithmetic_conservation": "arithmetic",
    "connector_position_accounting": "logic",
    "liquidation_health_accounting": "logic",
}

# Dispositions that are already terminal / resolved — a high-risk advisory hit on one of these is
# NOT re-routed (it is either already a finding, explicitly out of scope, or already in a deep pass).
TERMINAL_STATUSES = {"finding", "deferred_out_of_scope"}


def _policy() -> dict:
    try:
        return json.loads((ROOT / "config" / "agent_policy.json").read_text()).get("coverage_policy", {})
    except (OSError, json.JSONDecodeError):
        return {}


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _high_risk_ids_from_lenses() -> dict[str, str]:
    """manifest_id -> lens label, for every HIGH-RISK advisory hit found in the lens outputs present."""
    out_dir = audit_path("output")
    hits: dict[str, str] = {}

    # lenses exposing an explicit high_risk_manifest_ids list
    for fname, label in (("cross_function_invariant_audit.json", "cross_function_invariant"),
                         ("asset_source_consistency_audit.json", "asset_source_consistency"),
                         ("checkpoint_liveness_audit.json", "checkpoint_liveness")):
        d = _load_json(out_dir / fname)
        for mid in d.get("high_risk_manifest_ids", []) or []:
            hits.setdefault(mid, label)

    # recipient_custody: routed_to_bridge_custody_review
    d = _load_json(out_dir / "recipient_custody_audit.json")
    for mid in d.get("routed_to_bridge_custody_review", []) or []:
        hits.setdefault(mid, "recipient_custody")

    # cross_artifact_lifecycle: under-escalated items
    d = _load_json(out_dir / "cross_artifact_lifecycle_audit.json")
    for x in d.get("lifecycle_under_escalated", []) or []:
        mid = x.get("manifest_id") if isinstance(x, dict) else x
        if mid:
            hits.setdefault(mid, "cross_artifact_lifecycle")

    # griefing_dos: high-risk recommended review packets
    d = _load_json(out_dir / "griefing_dos_audit.json")
    for p in d.get("recommended_review_packets", []) or []:
        mid = p.get("manifest_id")
        if mid:
            hits.setdefault(mid, "griefing_dos")

    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    pol = _policy()
    full_audit = os.environ.get("AUDITWATCH_FULL_AUDIT") == "1"
    strict = pol.get("advisory_escalation_strict", False) or \
        (pol.get("advisory_escalation_strict_full_audit", True) and full_audit)
    override = os.environ.get("AUDITWATCH_ADVISORY_ESCALATION_OVERRIDE") == "1"

    man = _load_json(audit_path("output") / "coverage_manifest.json")
    man_idx = {i["id"]: i for i in man.get("items", [])}
    p, data, idx = ucd._load()

    candidate = _high_risk_ids_from_lenses()
    escalated, skipped = [], []
    for mid, label in sorted(candidate.items()):
        item = man_idx.get(mid)
        d = idx.get(mid)
        if not item or not d:
            continue
        surface = sft.item_text(item)
        cur = d.get("status")
        if not sft.is_high_risk_surface(surface):
            skipped.append({"manifest_id": mid, "lens": label, "reason": "surface not high-risk"}); continue
        # Skip only terminal/already-resolved states. Previously this required cur == "cleared", which
        # meant high-risk hits on unassigned/assigned items (the Panoptic case: 17 hits, 0 routed) were
        # never tagged for the deep-pass queue. Now any non-terminal hit is converted to needs_deep_pass.
        if cur in TERMINAL_STATUSES:
            skipped.append({"manifest_id": mid, "lens": label, "reason": f"terminal status ({cur})"}); continue
        if cur == "assigned" and d.get("assigned_pass") == "deep":
            skipped.append({"manifest_id": mid, "lens": label, "reason": "already needs_deep_pass"}); continue
        if d.get("advisory_escalation_justified") is True:
            skipped.append({"manifest_id": mid, "lens": label,
                            "reason": f"explicitly justified ({d.get('advisory_escalation_justification', 'no reason given')})"}); continue
        matched = sft.matched_terms(surface, sft.HIGH_RISK_ESCALATION_TERMS)
        specialist = LENS_SPECIALIST.get(label, "logic")
        rec = {"manifest_id": mid, "lens": label, "contract": item.get("contract"), "name": item.get("name"),
               "file": item.get("file"), "matched_term": matched, "required_specialist": specialist, "was": cur}
        if strict and not override:
            ucd.apply_update(d, "assigned", assigned_pass="deep", assigned_agent=specialist,
                             routed_reason=(f"advisory_escalation: high-risk {label} hit on a high-risk surface "
                                            f"({matched}) — resolve via {specialist} deep pass or file a finding"))
            # Structured provenance the deep-pass queue / ledger / report can read back.
            d["advisory_escalation"] = {"source_lens": label, "matched_term": matched,
                                        "file": item.get("file"), "function": item.get("name"),
                                        "required_specialist": specialist, "was": cur}
            rec["routed_to"] = "needs_deep_pass"
        else:
            rec["routed_to"] = "advisory_only"
        escalated.append(rec)

    # abi_getter_mismatch lens: route ITS OWN high/medium hits (routed_manifest_ids) WITHOUT the high-risk
    # surface filter — poolVote/claimRewards are not special_focus terms, so the generic loop above skips them.
    # The interface/public-getter ABI mismatch is itself the high-risk signal; route only confirmed mismatches.
    agm_strict = pol.get("abi_getter_mismatch_strict", False) or \
        (pol.get("abi_getter_mismatch_strict_full_audit", True) and full_audit)
    agm = _load_json(audit_path("output") / "abi_getter_mismatch_audit.json")
    agm_escalated = []
    for mid in agm.get("routed_manifest_ids", []) or []:
        item = man_idx.get(mid)
        d = idx.get(mid)
        if not item or not d:
            continue
        cur = d.get("status")
        rec = {"manifest_id": mid, "lens": "abi_getter_mismatch", "contract": item.get("contract"),
               "name": item.get("name"), "file": item.get("file"),
               "required_specialist": LENS_SPECIALIST["abi_getter_mismatch"], "was": cur}
        if cur in TERMINAL_STATUSES or (cur == "assigned" and d.get("assigned_pass") == "deep"):
            rec["routed_to"] = f"skipped ({cur})"
            agm_escalated.append(rec); continue
        if agm_strict and not override:
            ucd.apply_update(d, "assigned", assigned_pass="deep", assigned_agent="abi_getter_mismatch_review",
                             routed_reason=("abi_getter_mismatch: an interface declaration does not match the "
                                            "implementation's public-state-variable auto-getter ABI — verify the "
                                            "generated getter signature vs the interface signature and the call "
                                            "binding (prompts/deep_pass_packet.md), or file a finding"))
            d["abi_getter_mismatch"] = {"source_lens": "abi_getter_mismatch", "file": item.get("file"),
                                        "function": item.get("name"), "required_specialist": "logic", "was": cur}
            rec["routed_to"] = "needs_deep_pass"
        else:
            rec["routed_to"] = "advisory_only"
        agm_escalated.append(rec)

    # arithmetic_conservation lens: route ITS OWN high/medium hits (routed_manifest_ids) WITHOUT the
    # high-risk surface filter — calculate_rebase / _k are not special_focus terms, so the generic loop
    # above skips them. The conservation shape (multi-term supply aggregate / product-invariant rounding)
    # is itself the signal; route only the two-signal-confirmed hits.
    acn_strict = pol.get("arithmetic_conservation_strict", False) or \
        (pol.get("arithmetic_conservation_strict_full_audit", True) and full_audit)
    acn = _load_json(audit_path("output") / "arithmetic_conservation_audit.json")
    acn_escalated = []
    for mid in acn.get("routed_manifest_ids", []) or []:
        item = man_idx.get(mid)
        d = idx.get(mid)
        if not item or not d:
            continue
        cur = d.get("status")
        rec = {"manifest_id": mid, "lens": "arithmetic_conservation", "contract": item.get("contract"),
               "name": item.get("name"), "file": item.get("file"),
               "required_specialist": LENS_SPECIALIST["arithmetic_conservation"], "was": cur}
        if cur in TERMINAL_STATUSES or (cur == "assigned" and d.get("assigned_pass") == "deep"):
            rec["routed_to"] = f"skipped ({cur})"
            acn_escalated.append(rec); continue
        if acn_strict and not override:
            ucd.apply_update(d, "assigned", assigned_pass="deep", assigned_agent="arithmetic_conservation_review",
                             routed_reason=("arithmetic_conservation: a conservation surface the attack-surface "
                                            "scorer under-weights (multi-term supply/balance aggregate or "
                                            "product-invariant with integer division) — enumerate each term / "
                                            "factor and verify no double-count and no floor-to-zero rounding "
                                            "(prompts/deep_pass_packet.md), or file a finding"))
            d["arithmetic_conservation"] = {"source_lens": "arithmetic_conservation", "file": item.get("file"),
                                            "function": item.get("name"), "required_specialist": "arithmetic", "was": cur}
            rec["routed_to"] = "needs_deep_pass"
        else:
            rec["routed_to"] = "advisory_only"
        acn_escalated.append(rec)

    # connector_position_accounting lens: route ITS OWN net-new high/medium hits (routed_manifest_ids)
    # WITHOUT the high-risk surface filter — _getPositionTVL / updateHoldingPosition are not special_focus
    # terms. The connector/TVL/position-accounting shape is itself the signal (NOYA H-11/H-13/H-19/H-12).
    cpa_strict = pol.get("connector_position_accounting_strict", False) or \
        (pol.get("connector_position_accounting_strict_full_audit", True) and full_audit)
    cpa = _load_json(audit_path("output") / "connector_position_accounting_audit.json")
    cpa_escalated = []
    for mid in cpa.get("routed_manifest_ids", []) or []:
        item = man_idx.get(mid)
        d = idx.get(mid)
        if not item or not d:
            continue
        cur = d.get("status")
        rec = {"manifest_id": mid, "lens": "connector_position_accounting", "contract": item.get("contract"),
               "name": item.get("name"), "file": item.get("file"),
               "required_specialist": LENS_SPECIALIST["connector_position_accounting"], "was": cur}
        if cur in TERMINAL_STATUSES or (cur == "assigned" and d.get("assigned_pass") == "deep"):
            rec["routed_to"] = f"skipped ({cur})"
            cpa_escalated.append(rec); continue
        if cpa_strict and not override:
            ucd.apply_update(d, "assigned", assigned_pass="deep", assigned_agent="connector_position_accounting_review",
                             routed_reason=("connector_position_accounting: a connector TVL / position-accounting "
                                            "surface whose value depends on external protocol/registry state — "
                                            "enumerate each TVL term + its external reader + asset-vs-liability "
                                            "sign, re-derive product/division math, or verify the position-key "
                                            "identity (prompts/deep_pass_packet.md), or file a finding"))
            d["connector_position_accounting"] = {"source_lens": "connector_position_accounting",
                                                  "file": item.get("file"), "function": item.get("name"),
                                                  "required_specialist": "logic", "was": cur}
            rec["routed_to"] = "needs_deep_pass"
        else:
            rec["routed_to"] = "advisory_only"
        cpa_escalated.append(rec)

    # liquidation_health_accounting lens: route ITS OWN high-only hits (routed_manifest_ids) WITHOUT the
    # high-risk surface filter — the liquidation / health-CR / redemption / stability-pool accounting shape is
    # itself the signal (Size H-03/H-04/M-09/M-11; Ethos H-01/M-09/M-10). Internal helpers that a routed
    # entrypoint calls are carried as context_helpers (volume control), not routed separately. Never mints.
    lha_strict = pol.get("liquidation_health_accounting_strict", False) or \
        (pol.get("liquidation_health_accounting_strict_full_audit", True) and full_audit)
    lha = _load_json(audit_path("output") / "liquidation_health_accounting_audit.json")
    lha_ctx = lha.get("helper_attachments", {}) or {}
    lha_escalated = []
    for mid in lha.get("routed_manifest_ids", []) or []:
        item = man_idx.get(mid)
        d = idx.get(mid)
        if not item or not d:
            continue
        cur = d.get("status")
        helpers = lha_ctx.get(mid, [])
        rec = {"manifest_id": mid, "lens": "liquidation_health_accounting", "contract": item.get("contract"),
               "name": item.get("name"), "file": item.get("file"),
               "context_helpers": [h.get("function") for h in helpers],
               "required_specialist": LENS_SPECIALIST["liquidation_health_accounting"], "was": cur}
        if cur in TERMINAL_STATUSES or (cur == "assigned" and d.get("assigned_pass") == "deep"):
            rec["routed_to"] = f"skipped ({cur})"
            lha_escalated.append(rec); continue
        if lha_strict and not override:
            hint = (" review the attached internal helpers (" + ", ".join(rec["context_helpers"]) + ")"
                    if rec["context_helpers"] else "")
            ucd.apply_update(d, "assigned", assigned_pass="deep", assigned_agent="liquidation_health_accounting_review",
                             routed_reason=("liquidation_health_accounting: a liquidation / health-CR / redemption / "
                                            "stability-pool accounting surface — identify the collateral side, the "
                                            "debt side, and the health/CR/ICR/TCR/recovery-mode condition; verify "
                                            "CR/health checks before AND after the state mutation; trace the "
                                            "remainder/profit/fee/redistribution path (prompts/deep_pass_packet.md)"
                                            + hint + ", or file a finding"))
            d["liquidation_health_accounting"] = {"source_lens": "liquidation_health_accounting",
                                                  "file": item.get("file"), "function": item.get("name"),
                                                  "context_helpers": helpers,
                                                  "required_specialist": "logic", "was": cur}
            rec["routed_to"] = "needs_deep_pass"
        else:
            rec["routed_to"] = "advisory_only"
        lha_escalated.append(rec)

    # P311: promoted recall lenses — ADVISORY-ONLY surfacing. Read each lens's candidates[] and report them as
    # routed_to:"advisory_only". This NEVER calls ucd.apply_update, NEVER flips a disposition, NEVER routes/gates —
    # it only surfaces the hits for the review gate / specialists. Kept in a SEPARATE set from the strict-routing
    # lenses above so it can never enter the apply_update path (advisory-only pending generalization validation).
    PROMOTED_ADVISORY_LENSES = {
        "nonstandard_permit": "token_integration", "erc4626_limit_fidelity": "erc4626",
        "eip712_domain_separator_staleness": "token_integration", "beneficiary_guard_parity": "semantic_guard",
        "admin_capability_parity": "semantic_guard", "crosschain_min_gas_unchecked": "cross_chain",
        "crosschain_refund_recipient": "cross_chain", "fee_wrapper_bypass": "access_control",
    }
    promoted_advisory_hits = []
    for lens, specialist in PROMOTED_ADVISORY_LENSES.items():
        d = _load_json(audit_path("output") / f"{lens}_audit.json")
        for c in d.get("candidates", []) or []:
            mid = c.get("manifest_id")
            item = man_idx.get(mid) if mid else None
            promoted_advisory_hits.append({
                "manifest_id": mid, "lens": lens, "confidence": c.get("confidence"),
                "finding_shape": c.get("finding_shape"),
                "contract": (item or {}).get("contract") or c.get("contract"),
                "name": (item or {}).get("name") or c.get("function"),
                "file": (item or {}).get("file") or c.get("file"),
                "required_specialist": specialist, "routed_to": "advisory_only"})

    routed = [e for e in escalated if e.get("routed_to") == "needs_deep_pass"]
    agm_routed = [e for e in agm_escalated if e.get("routed_to") == "needs_deep_pass"]
    acn_routed = [e for e in acn_escalated if e.get("routed_to") == "needs_deep_pass"]
    cpa_routed = [e for e in cpa_escalated if e.get("routed_to") == "needs_deep_pass"]
    lha_routed = [e for e in lha_escalated if e.get("routed_to") == "needs_deep_pass"]
    if routed or agm_routed or acn_routed or cpa_routed or lha_routed:
        p.write_text(json.dumps(data, indent=2))

    report = {
        "gate": "advisory_escalation", "strict": strict, "override_active": override, "full_audit": full_audit,
        "candidates": len(candidate), "escalated": len(escalated),
        "routed_to_deep_pass": len(routed), "skipped": len(skipped),
        "escalations": escalated, "skipped_detail": skipped,
        "abi_getter_mismatch_strict": agm_strict,
        "abi_getter_mismatch_routed": len(agm_routed),
        "abi_getter_mismatch_escalations": agm_escalated,
        "arithmetic_conservation_strict": acn_strict,
        "arithmetic_conservation_routed": len(acn_routed),
        "arithmetic_conservation_escalations": acn_escalated,
        "connector_position_accounting_strict": cpa_strict,
        "connector_position_accounting_routed": len(cpa_routed),
        "connector_position_accounting_escalations": cpa_escalated,
        "liquidation_health_accounting_strict": lha_strict,
        "liquidation_health_accounting_routed": len(lha_routed),
        "liquidation_health_accounting_escalations": lha_escalated,
        "promoted_advisory_lenses": sorted(PROMOTED_ADVISORY_LENSES),
        "promoted_advisory_routed": 0,  # advisory-only: NEVER routes/gates (pending generalization validation)
        "promoted_advisory_lens_hits": promoted_advisory_hits,
    }
    (audit_path("output") / "advisory_escalation_gate.json").write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print("Advisory escalation gate: " + ("STRICT" if strict else "advisory") + (" (OVERRIDE)" if override else ""))
        print(f"  high-risk advisory hits {len(candidate)} · escalated {len(escalated)} · "
              f"routed→needs_deep_pass {len(routed)} · skipped {len(skipped)}")
        for e in routed:
            print(f"   → {e['contract']}.{e['name']} ({e['lens']}, {e['was']} → needs_deep_pass, "
                  f"specialist={e['required_specialist']})")
        if agm_escalated:
            print(f"  abi_getter_mismatch ({'STRICT' if agm_strict else 'advisory'}): "
                  f"routed→needs_deep_pass {len(agm_routed)} of {len(agm_escalated)}")
            for e in agm_routed:
                print(f"   → {e['contract']}.{e['name']} (abi_getter_mismatch, {e['was']} → needs_deep_pass)")
        if acn_escalated:
            print(f"  arithmetic_conservation ({'STRICT' if acn_strict else 'advisory'}): "
                  f"routed→needs_deep_pass {len(acn_routed)} of {len(acn_escalated)}")
            for e in acn_routed:
                print(f"   → {e['contract']}.{e['name']} (arithmetic_conservation, {e['was']} → needs_deep_pass)")
        if cpa_escalated:
            print(f"  connector_position_accounting ({'STRICT' if cpa_strict else 'advisory'}): "
                  f"routed→needs_deep_pass {len(cpa_routed)} of {len(cpa_escalated)}")
            for e in cpa_routed:
                print(f"   → {e['contract']}.{e['name']} (connector_position_accounting, {e['was']} → needs_deep_pass)")
        if lha_escalated:
            print(f"  liquidation_health_accounting ({'STRICT' if lha_strict else 'advisory'}): "
                  f"routed→needs_deep_pass {len(lha_routed)} of {len(lha_escalated)}")
            for e in lha_routed:
                ctx = f"  +{len(e['context_helpers'])} helper-ctx" if e.get("context_helpers") else ""
                print(f"   → {e['contract']}.{e['name']} (liquidation_health_accounting, {e['was']} → needs_deep_pass){ctx}")
        if promoted_advisory_hits:
            print(f"  promoted recall lenses (ADVISORY-ONLY, never routes): {len(promoted_advisory_hits)} hits "
                  f"across {len(set(h['lens'] for h in promoted_advisory_hits))} lenses (see promoted_advisory_lens_hits)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
