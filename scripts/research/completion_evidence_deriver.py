#!/usr/bin/env python3
"""P279 — completion-stage evidence deriver (RESEARCH-ONLY, ADVISORY, UN-WIRED).

Fills the PoC-readiness evidence fields the recall harness leaves as 'operator-to-derive', deriving them from
SOURCE-DERIVED data only: the coverage-manifest function metadata (signature/visibility/mutability/modifiers/
external_calls/has_loop/tags) + the candidate's class label. Each derived field carries value + confidence
(HIGH/MEDIUM/LOW) + source_basis. Confidence is ANOMALY-based (config-mutation-without-auth, has_loop, external_calls),
not mere capability, to keep READY low-noise. NEVER reads award text; NEVER sets severity/reportability.

Usage:
  python scripts/research/completion_evidence_deriver.py --manifest <coverage_manifest.json> \
      --packages <evidence_packages.json> --out <derived_evidence_packages.json> [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source_span_guard_extractor as _ssx  # noqa: E402
import cross_function_value_tracer as _cfvt  # noqa: E402
import invariant_delta_deriver as _idd  # noqa: E402  (P284 corrected-reference / invariant-delta)

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "config/research_completion_evidence_deriver.json").read_text())
LABEL = "SUPERVISED_EVAL"
PLACE = {str(x).strip().lower() for x in CFG["placeholder_markers"]}
AUTH = CFG["auth_modifier_patterns"]
VMOVE = CFG["value_movement_terms"]
CFGTAGS = set(CFG["config_mutation_tags"])
RO = set(CFG["readonly_mutability"])
# P291 Part A: EXTERNAL_INTEGRATION source-backed deviation signals
_INTEG_LOWLEVEL = [m.lower() for m in CFG.get("integration_lowlevel_call_markers", [])]
_INTEG_CALLBACK = [m.lower() for m in CFG.get("integration_callback_markers", [])]
_INTEG_GUARD = [m.lower() for m in CFG.get("integration_reentrancy_guard_markers", [])]
_INTEG_STATE_WRITE = re.compile(CFG.get("integration_state_write_regex", r"\b[\w.\[\]]+\s*(?:=|\+=|-=)\s*[^=]"))


def _integration_deviation_evidence(item: dict, body: str, pkg: dict) -> dict:
    """P291: source-backed EXTERNAL_INTEGRATION deviation. AUTO-detect ONLY unambiguous low-level/callback/
    reentrancy-ordering signals; structural bases need an EXPLICIT operator field. Mere safeTransferFrom / nonReentrant
    transfer / external visibility never qualify. Fail-closed."""
    stamp = {"is_gate": False, "research_only": True, "emits_findings": False}
    # explicit operator-supplied deviation (e.g. fee-on-transfer/adapter/create2/cross-contract) — never auto-guessed
    op = pkg.get("integration_deviation_evidence")
    if isinstance(op, dict) and op.get("deviation_present") is True and _present(op.get("basis")):
        return dict(stamp, deviation_present=True, basis=str(op.get("basis")), source="operator_explicit",
                    detail=str(op.get("detail", ""))[:200])
    b = _ssx.strip_comments(body or "").lower()
    lowlevel = any(m in b for m in _INTEG_LOWLEVEL)
    callback = any(m in b for m in _INTEG_CALLBACK)
    guarded = any(m in b for m in _INTEG_GUARD)
    if lowlevel or callback:
        # reentrancy-ordering subtype: low-level external call with no reentrancy guard + a state write present
        reentrancy = lowlevel and not guarded and bool(_INTEG_STATE_WRITE.search(_ssx.strip_comments(body or "")))
        basis = ("low_level_call_or_callback" if not reentrancy else "reentrancy_ordering_no_guard")
        return dict(stamp, deviation_present=True, basis=basis, source="auto_source",
                    detail=("low-level call/callback surface" + ("; ext-call w/o reentrancy guard + state write"
                                                                 if reentrancy else "")))
    return dict(stamp, deviation_present=False, basis=None, source="none",
                detail="no low-level call / callback / reentrancy-ordering signal; mere transfer/visibility is not a "
                       "deviation")
FORBIDDEN = ("severity", "reportable", "submission_ready", "concluded", "emits_finding", "production_routing")


class FailClosed(Exception):
    pass


def _present(v) -> bool:
    if v is None:
        return False
    if isinstance(v, (list, dict)):
        return len(v) > 0
    s = str(v).strip().lower()
    return s not in PLACE and "operator-to-derive" not in s and "operator to derive" not in s and len(s) > 0


def _state_changing(item: dict) -> bool:
    return str(item.get("mutability", "")).strip().lower() not in RO


def _has_auth(item: dict) -> bool:
    mods = " ".join(item.get("modifiers", []) or []).lower()
    return any(p in mods for p in AUTH)


def _value_move(item: dict, fn: str) -> bool:
    sig = (str(item.get("signature", "")) + " " + fn).lower()
    tagset = {str(t).lower() for t in (item.get("tags") or [])}
    return any(t in sig for t in VMOVE) or bool(tagset & {"accounting", "token", "reward"}) or \
        bool(item.get("external_calls"))


def _f(value, conf, basis, assum=None):
    return {"value": value, "confidence": conf, "source_basis": basis, "unresolved_assumptions": assum or []}


def derive(pkg: dict, item: dict | None) -> dict:
    cls = pkg.get("award_class", "UNKNOWN_OTHER")
    cf = pkg.get("contract_function", "?")
    contract, _, fn = cf.partition(".")
    if not item:
        # no manifest signal -> everything LOW / unresolved (cannot reach READY)
        nf = lambda v: _f(v, "LOW", "no manifest item joined", ["no source metadata for this locus"])
        d = {k: nf("operator-to-derive") for k in CFG["derived_fields"]}
        d["transaction_sequence"] = _f(f"call {cf}(...)", "LOW", "candidate locus only")
        return d, "no_manifest_item"

    sig = str(item.get("signature", ""))
    vis = str(item.get("visibility", "")).lower()
    external_reachable = vis in ("external", "public")
    state = _state_changing(item)
    auth = _has_auth(item)
    ext_calls = bool(item.get("external_calls"))
    loop = bool(item.get("has_loop"))
    tagset = {str(t).lower() for t in (item.get("tags") or [])}
    vmove = _value_move(item, fn)
    basis_core = f"manifest: visibility={vis}, mutability={item.get('mutability') or 'nonpayable'}, " \
                 f"modifiers={item.get('modifiers')}, external_calls={ext_calls}, has_loop={loop}, tags={sorted(tagset)}"

    # ---- attacker_path (anomaly-based) ----
    ap_conf, ap_val, ap_assum = "LOW", "", []
    if external_reachable and state and auth:
        # any authority-modifier-guarded function is NOT a clean unauthorized attacker entry; bypass is a CORE claim
        ap_conf = "LOW"
        ap_val = f"{cf} is guarded by modifier(s) {item.get('modifiers')}; not a direct unauthorized entry"
        ap_assum = [f"a bypass of {item.get('modifiers')} would be the CORE exploitability claim - needs source review"]
    elif external_reachable and state:
        if cls == "ACCESS_CONTROL_AUTHORIZATION":
            if not auth and (tagset & CFGTAGS):
                ap_conf, ap_val = "HIGH", f"unauthorized EOA calls {cf}: external state-changing config/param mutator with NO authority modifier"
            elif not auth:
                ap_conf, ap_val = "MEDIUM", f"unauthorized EOA calls {cf}: external state-changing, no authority modifier"
            else:
                ap_conf, ap_val, ap_assum = "LOW", f"{cf} is guarded by a modifier", ["guard may be bypassable - needs source review"]
        elif cls == "DOS_LIVENESS":
            if loop:
                ap_conf, ap_val = "HIGH", f"attacker grows an enumerable/looped set then {cf} reverts/exhausts gas (has_loop)"
            else:
                ap_conf, ap_val, ap_assum = "MEDIUM", f"attacker triggers {cf} to block progress", ["no loop signal; blockage path needs source review"]
        elif cls == "EXTERNAL_INTEGRATION":
            if ext_calls:
                ap_conf, ap_val = "HIGH", f"attacker controls the external call / callback reached from {cf} (external_calls)"
            else:
                ap_conf, ap_val, ap_assum = "MEDIUM", f"attacker exercises integration path in {cf}", ["no external-call signal in manifest"]
        elif cls in ("ORDER_VALIDATION", "FRONT_RUNNING_MEV"):
            sl = (sig + " " + fn).lower()
            if any(t in sl for t in ("order", "fill", "cancel", "swap", "settle", "quote")):
                ap_conf, ap_val = "MEDIUM", f"attacker fills/cancels/orders via {cf} before/instead of the intended party"
            else:
                ap_conf, ap_val, ap_assum = "LOW", f"order-validation anomaly in {cf} not visible from manifest", \
                    ["order-state/recipient-binding anomaly needs source review (CORE)"]
        else:  # ACCOUNTING / MATH / ORACLE / REWARDS — the anomaly is a value-flow/invariant fact NOT in the manifest
            ap_conf, ap_val = "LOW", f"attacker calls {cf} with chosen inputs ({sig[:60]})"
            ap_assum = ["value-flow / invariant anomaly NOT visible from manifest metadata - needs value-flow "
                        "derivation (CORE exploitability claim unresolved)"]
    else:
        ap_val, ap_assum = f"{cf} is {vis}/{item.get('mutability') or ''} - not a direct attacker entry", ["not externally reachable or read-only"]

    # ---- attacker_controlled_inputs ----
    aci = _f(f"msg.sender + args of {sig[:80]}", "HIGH" if external_reachable else "LOW",
             "manifest signature + visibility")

    # ---- impact_delta ----
    if not state:
        idd = _f("read-only - no state delta", "LOW", "mutability is view/pure")
    elif ext_calls or (tagset & {"accounting", "token", "reward"}) or vmove:
        idd = _f(f"state/value mutation in {contract} via {fn} ({'external value movement' if ext_calls else 'value-moving op'})",
                 "HIGH", basis_core)
    else:
        idd = _f(f"state mutation in {contract}.{fn}", "MEDIUM", basis_core)

    # ---- victim_gainer ----
    if vmove:
        vg = _f(f"victim = users/LPs of {contract} (value moved); gainer = attacker/recipient", "MEDIUM",
                "value-movement signal (name/tags/external_calls)")
    elif cls == "ACCESS_CONTROL_AUTHORIZATION" and ap_conf in ("HIGH", "MEDIUM"):
        # an access anomaly's victim is whoever the unauthorized state/config change harms (no value transfer needed)
        vg = _f(f"victim = users/protocol governed by the state/config {cf} mutates; gainer = unauthorized caller",
                "MEDIUM", "access-control anomaly: victim is the protected-state stakeholder")
    else:
        vg = _f("unclear from manifest signals", "LOW", "no value-movement signal",
                ["who-loses/gains needs source value-flow review"])

    # ---- terminality ----
    term = _f("repeatable while callable" + (" ; durable if state corruption" if state else ""),
              "MEDIUM" if state else "LOW", "state-changing + externally reachable")

    # ---- tx_sequence ----
    tx = _f([f"attacker calls {cf} with chosen args"], "HIGH", "manifest signature")

    # ---- invariants + assertion + refutation (class template) ----
    inv_exp, inv_brk, assertion, refute = _class_invariant(cls, cf, contract)

    d = {
        "attacker_path": _f(ap_val, ap_conf, basis_core, ap_assum),
        "attacker_controlled_inputs": aci,
        "impact_delta": idd,
        "victim_gainer": vg,
        "terminality_or_amplification": term,
        "transaction_sequence": tx,
        "invariant_expected": _f(inv_exp, "MEDIUM", "class template"),
        "invariant_broken": _f(inv_brk, "MEDIUM", "class template"),
        "poc_assertion": _f(assertion, "MEDIUM", "class template + locus"),
        "refutation_questions": _f(refute, "MEDIUM", "class template"),
        "poc_tier_recommendation": _f("partial_runtime" if ext_calls or loop else "inherit_and_expose_internal",
                                      "MEDIUM", "manifest complexity signals"),
        "unresolved_assumptions": _f(ap_assum + (["value-flow anomaly unverified"] if cls in
                                     ("ACCOUNTING_LIQUIDATION_BAD_DEBT", "SHARE_ROUNDING_PRECISION",
                                      "ORACLE_PRICING", "REWARDS_CLAIMS") else []), "LOW", "derivation residue"),
    }
    return d, "derived"


def _class_invariant(cls, cf, contract):
    T = {
        "ACCESS_CONTROL_AUTHORIZATION": (
            f"only an authorized principal may execute the state-changing path in {cf}",
            f"an unauthorized caller mutates protected state via {cf}",
            f"assert an unauthorized EOA can call {cf} and change protected state that should be restricted",
            "Is there an internal/inherited guard not captured as a modifier? Is the mutated state actually sensitive?"),
        "DOS_LIVENESS": (
            f"{cf} and dependent claim/withdraw/redeem paths always make progress",
            f"an attacker-controlled entry makes {cf} (or a dependent path) permanently/repeatedly revert or exhaust gas",
            f"assert one attacker-controlled state entry causes {cf} (or a victim path) to revert / not progress",
            "Is the loop bounded by a trusted set? Is there an alternate unblocked path?"),
        "EXTERNAL_INTEGRATION": (
            f"the external call/callback reached from {cf} cannot break {contract} internal accounting",
            f"a malicious external return/callback desyncs {contract} state or redirects value",
            f"assert a crafted external/callback response leaves {contract} state inconsistent or value misrouted",
            "Is the external target trusted/whitelisted? Is there reentrancy/return-value validation?"),
        "ORDER_VALIDATION": (
            "an order can only be filled/cancelled by the entitled party under its terms",
            f"{cf} lets a non-entitled party fill/redirect/replay the order",
            f"assert an attacker-controlled call to {cf} violates the maker/taker/order-state invariant",
            "Are nonce/deadline/signature checks present? Is recipient bound to the maker?"),
        "FRONT_RUNNING_MEV": (
            "settlement/quote used by the order is not attacker-manipulable in the same tx/block",
            f"{cf} settlement can be front-run / uses a stale or attacker-movable quote",
            f"assert reordering around {cf} extracts value or invalidates the intended fill",
            "Is the quote committed/au-snapshotted? Is slippage enforced?"),
        "SHARE_ROUNDING_PRECISION": (
            f"share<->asset conversion in {cf} conserves value up to <=1 unit and never nets the actor positive",
            f"{cf} rounding/precision lets a round-trip net the actor more than input or strand funds",
            f"assert a crafted-amount round-trip through {cf} nets the actor > input (or strands funds)",
            "Does every path round toward the protocol? Is the dust bounded and benign?"),
        "ACCOUNTING_LIQUIDATION_BAD_DEBT": (
            f"post-{cf} accounting equals the conservation/corrected reference (position == global; no residue)",
            f"{cf} leaves position/global mismatch, bad-debt residue, or mis-allocated collateral/fees",
            f"assert post-{cf} accounting differs from the conservation reference",
            "Is the accounting set vs incremented consistently? Is there a corrected reference to compare?"),
        "ORACLE_PRICING": (
            f"{cf} uses a fresh, correct, non-manipulable valuation",
            f"{cf} uses a stale/wrong/manipulable price -> mis-valuation",
            f"assert {cf} consumes a manipulated/stale price and produces a wrong valuation/decision",
            "Is staleness/sequencer checked? Is the source spot-manipulable?"),
        "REWARDS_CLAIMS": (
            f"rewards via {cf} go to the entitled claimant once, at the correct snapshot",
            f"{cf} mis-routes, double-pays, blocks, or snapshot-games rewards",
            f"assert {cf} pays the wrong recipient / double / blocked / stale-snapshot amount",
            "Is the claimant bound? Is the accumulator updated before transfer? Idempotent?"),
    }
    return T.get(cls, (
        f"{cf} preserves the relevant protocol invariant",
        f"{cf} violates the relevant protocol invariant",
        f"assert {cf} produces an outcome inconsistent with its intended invariant",
        "What is the precise invariant and corrected reference?"))


def _guard_inputs(pkg: dict) -> None:
    for f in CFG["forbidden_input_fields"]:
        if f in pkg and f != "title":  # 'title' may legitimately be absent; never read it as signal regardless
            # presence is allowed but it must never be used; we simply never read it. Flag award-text leakage attempts:
            if f in ("award_title", "award_body", "ak_title", "reveal", "answer_key", "scoring"):
                raise FailClosed(f"forbidden award-text field '{f}' present in deriver input")


def run(manifest_path: Path, packages_path: Path, out_path: Path, quiet: bool) -> int:
    man = _load(manifest_path)
    pkgs_doc = _load(packages_path)
    if man is None or pkgs_doc is None:
        raise FailClosed("missing/unreadable manifest or packages")
    index = {f"{i.get('contract')}.{i.get('name')}": i for i in man.get("items", []) if i.get("kind") == "function"}
    trace_index = _cfvt.build_index(man)  # P283: name -> [items] for cross-function tracing
    pkgs = pkgs_doc.get("packages") if isinstance(pkgs_doc, dict) else pkgs_doc
    if not isinstance(pkgs, list):
        raise FailClosed("packages must be a list")

    out_pkgs = []
    for p in pkgs:
        _guard_inputs(p)
        item = index.get(p.get("contract_function"))
        derived, kind = derive(p, item)
        # write derived values into the gate-field names (replace operator-to-derive placeholders); keep confidence map
        enriched = dict(p)
        enriched["attacker_model"] = derived["attacker_path"]["value"]
        enriched["attacker_controlled_inputs"] = derived["attacker_controlled_inputs"]["value"]
        enriched["state_value_liveness_delta"] = derived["impact_delta"]["value"]
        enriched["victim_gainer"] = derived["victim_gainer"]["value"]
        enriched["terminality_or_amplification"] = derived["terminality_or_amplification"]["value"]
        enriched["tx_sequence"] = derived["transaction_sequence"]["value"]
        enriched["invariant_expected"] = derived["invariant_expected"]["value"]
        enriched["invariant_broken"] = derived["invariant_broken"]["value"]
        enriched["poc_assertion"] = derived["poc_assertion"]["value"]
        enriched["refutation_result"] = "questions: " + derived["refutation_questions"]["value"]
        enriched["poc_feasibility_tier"] = derived["poc_tier_recommendation"]["value"]
        enriched["unresolved_assumptions"] = derived["unresolved_assumptions"]["value"]
        enriched["evidence_source"] = "auto_derived_p279"
        enriched["derivation_kind"] = kind
        enriched["derived_confidence"] = {k: {"confidence": v["confidence"], "source_basis": v["source_basis"]}
                                          for k, v in derived.items()}
        # P281: attach source-span gate evidence (D1 inline guard / D2 state-machine / D3 value-flow / D4 source-span).
        # Tolerant: when the body is unresolvable, gate_evidence.body_available=False -> gate falls back to P279 path.
        try:
            ge = _ssx.extract(item, None) if item else {"body_available": False}
        except Exception:
            ge = {"body_available": False, "reason": "extractor error"}
        enriched["gate_evidence"] = ge
        # P291 Part A: EXTERNAL_INTEGRATION source-backed deviation evidence (gate requires it before READY).
        if p.get("award_class") == "EXTERNAL_INTEGRATION" and item and ge.get("body_available") \
                and not ge.get("is_declaration_only"):
            try:
                body_txt = _ssx.extract_body(item, None).get("body", "")
                enriched["integration_deviation_evidence"] = _integration_deviation_evidence(item, body_txt, p)
            except Exception:
                enriched["integration_deviation_evidence"] = {"deviation_present": False, "basis": None,
                                                              "source": "error"}
        # P282 D3: structured value-flow evidence (source-span derived; confidence by anomaly, not mere movement).
        if ge.get("body_available") and not ge.get("is_declaration_only"):
            anomaly = ge.get("value_anomaly_div_before_mul")
            vf_present = ge.get("value_flow_detected")
            out_of_span = ge.get("value_flow_out_of_span")
            conf = "MEDIUM" if (vf_present and anomaly) else "LOW"
            enriched["value_flow_evidence"] = {
                "value_flow_summary": ("division-before-multiplication ordering anomaly on a value computation"
                                       if anomaly else
                                       "value-flow lives in a delegated callee (out of this span)" if out_of_span else
                                       "value-flow present (state write / asset move) but no source-detectable anomaly"
                                       if vf_present else "no concrete value-flow in this span"),
                "attacker_input_to_state_link": ("external entry + in-span state write" if ge.get("state_write")
                                                 else "unclear (no in-span state write)"),
                "affected_variables": ge.get("value_markers", []),
                "value_movement_or_accounting_write": bool(ge.get("state_write") or ge.get("asset_move")),
                "expected_invariant": "value conservation / correct rounding for the computation" if anomaly else None,
                "broken_invariant_hypothesis": "rounding loss from div-before-mul strands/mis-allocates value"
                                               if anomaly else None,
                "confidence": conf,
                "source_basis": f"source span {ge.get('source_span')} of {ge.get('file')}",
                "unresolved_assumptions": ([] if anomaly else
                                           ["value-flow is in a delegated callee; needs cross-function tracing (CORE)"]
                                           if out_of_span else
                                           ["no source-detectable anomaly; the broken invariant needs data-flow/"
                                            "corrected-reference reasoning (CORE)"])}
            # P283 V2: when the in-span scan has no anomaly, trace bounded callees for a cross-function anomaly.
            if not anomaly and item:
                try:
                    enriched["trace_evidence"] = _cfvt.trace(item, trace_index, None)
                except Exception:
                    enriched["trace_evidence"] = {"trace_status": "TRACE_UNRESOLVED", "value_flow_confidence": "LOW"}
            # P284: corrected-reference / invariant-delta derivation against SOURCE-BACKED references (sibling /
            # registry / rounding / oracle / state-machine). On a FOUND deviation at HIGH|MEDIUM for a value/state
            # class, upgrade the core readiness fields from that reference so the candidate can reach READY via the
            # normal path. NEVER on NO_REFERENCE / AMBIGUOUS / INSUFFICIENT (those stay blocked).
            if item:
                item_id = dict(item)
                item_id["award_class"] = p.get("award_class")
                try:
                    idr = _idd.derive(item_id, man, None, ge, enriched.get("trace_evidence"))
                except Exception:
                    idr = None
                if idr:
                    enriched["invariant_delta_evidence"] = idr
                    cls_ok = p.get("award_class") in (_idd.VALUE_CLASSES | _idd.STATE_CLASSES)
                    if (cls_ok and idr["invariant_delta_status"] in _idd.LIFT_STATUSES
                            and str(idr["confidence"]).upper() in ("HIGH", "MEDIUM")):
                        conf = str(idr["confidence"]).upper()
                        enriched["attacker_model"] = idr["attacker_influence_link"] or enriched.get("attacker_model")
                        enriched["state_value_liveness_delta"] = (idr["delta_hypothesis"]
                                                                  or enriched.get("state_value_liveness_delta"))
                        enriched["victim_gainer"] = idr["victim_gainer"] or enriched.get("victim_gainer")
                        enriched["invariant_broken"] = (idr["expected_expression_or_flow"]
                                                        or enriched.get("invariant_broken"))
                        enriched["poc_assertion"] = idr["poc_assertion"] or enriched.get("poc_assertion")
                        # P293: a source-backed cross-function reward-index lift also supplies the two base dims that
                        # admitted internal-locus packages lack (root_cause / runner_up_mechanism). Scoped to the
                        # P293 lens and fill-if-missing only — never overrides an existing dimension on any package.
                        if idr.get("lens_name") == "reward_index_cross":
                            enriched["root_cause"] = enriched.get("root_cause") or (
                                f"{idr.get('lens3_pattern')}: " + (idr.get("missing_or_incorrect_snapshot_basis")
                                or idr.get("observed_expression_or_flow") or "reward-index deviation"))
                            enriched["runner_up_mechanism"] = enriched.get("runner_up_mechanism") or (
                                "single source-backed reward-index deviation; no competing mechanism on this path")
                        dc = enriched.get("derived_confidence") or {}
                        for core in ("attacker_path", "impact_delta", "victim_gainer"):
                            if str((dc.get(core) or {}).get("confidence", "")).upper() not in ("HIGH", "MEDIUM"):
                                dc[core] = {"confidence": conf,
                                            "source_basis": "P284 invariant-delta: " + (idr["source_basis"] or "")[:160]}
                        enriched["derived_confidence"] = dc
        # advisory contract stamp
        for f in FORBIDDEN:
            enriched[f] = False
        enriched["severity"] = None
        out_pkgs.append(enriched)

    viol = [{"id": p.get("candidate_id"), "field": f} for p in out_pkgs for f in FORBIDDEN if p.get(f) not in (False, None)]
    guard = {"module": "completion_evidence_deriver", "result": "PASS" if not viol else "FAIL",
             "guard_violations": len(viol), "violations": viol}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    (out_path.parent / "deriver_guard_report.json").write_text(json.dumps(guard, indent=2))
    if viol:
        raise FailClosed("guard violation")
    out = {"label": LABEL, "mode": "SUPERVISED_EVAL_DERIVED_EVIDENCE", "is_gate": False, "research_only": True,
           "emits_findings": False, "packages": out_pkgs}
    out_path.write_text(json.dumps(out, indent=2))
    if not quiet:
        from collections import Counter
        ck = Counter(p["derived_confidence"]["attacker_path"]["confidence"] for p in out_pkgs)
        print(f"[p279:deriver] {len(out_pkgs)} packages; attacker_path confidence {dict(ck)}")
    return 0


def _load(p: Path):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--packages", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    try:
        run(Path(a.manifest), Path(a.packages), Path(a.out), a.quiet)
    except FailClosed as e:
        print(f"[completion_evidence_deriver] FAIL-CLOSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
