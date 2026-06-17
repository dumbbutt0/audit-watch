#!/usr/bin/env python3
"""P284 — corrected-reference / invariant-delta deriver (RESEARCH-ONLY, ADVISORY, UN-WIRED).

P283 proved lexical anomaly detection is exhausted: cross-function tracing finds value-flow but not the VIOLATION,
because the bug is a RELATIONSHIP error (wrong recipient/ledger/order/rounding, missing symmetric update, global-vs-
position mismatch, value not applied, stale-state value), not a token error. This module derives value-bug evidence by
comparing a candidate's observed value-flow against a SOURCE-BACKED reference, NEVER an invented one:

  D4.1 conservation invariant       (local bounded-SSA equation)
  D4.2 symmetric ledger update      (registry_position_lifecycle_taxonomy.classify_contract)   [precision spine]
  D4.3 sibling-function reference   (sibling_function_parity_taxonomy.classify_pair)            [precision spine]
  D4.4 corrected-reference expr     (omitted_term_dataflow_gate._term_flow + bound_semantics_gate._rounding_evidence)
  D4.5 before/after delta equation  (local bounded-SSA equation)
  D4.6 oracle normalization         (local pattern over oracle markers)
  D4.7 state-machine value invariant(P281 state-machine evidence + or-state gate)

The validated 0-FP detectors are imported READ-ONLY as pure evidence helpers; this module never edits/routes/wires them.
A candidate is liftable ONLY when a 0-FP DEVIATION is found (sibling missing-component / registry desync / computed-
unapplied / rounding-direction / forbidden-state value mutation) — a local before/after equation supplies the PoC
assertion but never lifts on its own. Bounded-SSA is an INTERNAL method only (no compiler SSA / alias / symbolic / SMT).

Importable: derive(item, manifest, audit_id, gate_evidence, trace_evidence) -> invariant_delta record (advisory-stamped).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))           # reused detector platform (read-only)
sys.path.insert(0, str(Path(__file__).resolve().parent))  # P281-P283 chain
import source_span_guard_extractor as _ssx  # noqa: E402
import sibling_function_parity_taxonomy as _sfp  # noqa: E402
import registry_position_lifecycle_taxonomy as _rpl  # noqa: E402
import omitted_term_dataflow_gate as _otd  # noqa: E402
import bound_semantics_gate as _bsg  # noqa: E402

CFG = json.loads((ROOT / "config/research_invariant_delta_deriver.json").read_text())
LIFT_STATUSES = set(CFG["lift_statuses"])
ALL_STATUSES = set(CFG["all_statuses"])
VALUE_CLASSES = set(CFG["value_classes"])
STATE_CLASSES = set(CFG["state_classes"])
MAX_SIB = int(CFG["max_siblings_examined"])
SIB_LIFT_CONF = set(CFG["sibling_liftable_confidence"])
_TOTAL = re.compile(CFG["total_state_regex"])
_BAL = re.compile(r"\b(\w*balanceof\w*|balancebefore|balanceafter|\w+before|\w+after)\b", re.I)
ORACLE = [m.lower() for m in CFG["oracle_markers"]]
ORACLE_NORM = [m.lower() for m in CFG["oracle_normalization_markers"]]
ORACLE_STALE = [m.lower() for m in CFG["oracle_staleness_markers"]]
# P289 loss/reward lens signal sets (generic Solidity vocabulary — NO target/award constants)
L_STAKE = CFG["lens_stake_verbs"]
L_LOSS = CFG["lens_loss_terms"]
L_INDEX = CFG["lens_index_terms"]
L_UWRITE = CFG["lens_user_write_markers"]
L_LOSS_EVT = CFG["lens_loss_event_verbs"]
L_GLOBAL = CFG["lens_global_accumulator_markers"]
L_PERKEY = CFG["lens_per_key_markers"]
L_REWARD = CFG["lens_reward_path_terms"]
L_XFER = CFG["lens_transfer_markers"]
L_SHARE = CFG["lens_share_terms"]
_SAMEBLOCK_GUARD = re.compile(CFG["lens_sameblock_guard_regex"])
# P293 cross-function reward-index lens families (config-driven; generic vocabulary; NO target/award constants)
L3_USER_SHARE = [t.lower() for t in CFG["lens3_user_share_terms"]]
L3_GLOBAL_SHARE = [t.lower() for t in CFG["lens3_global_share_terms"]]
L3_GLOBAL_INDEX = [t.lower() for t in CFG["lens3_global_index_terms"]]
L3_USER_INDEX = [t.lower() for t in CFG["lens3_user_index_terms"]]
L3_PENDING = [t.lower() for t in CFG["lens3_pending_terms"]]
L3_INIT = [t.lower() for t in CFG["lens3_init_markers"]]
L3_LOSS = [t.lower() for t in CFG["lens3_loss_terms"]]
L3_MAX_SIB = int(CFG["lens3_max_sibling_scan"])
# a per-user share/balance/stake/deposit mutation (struct field write OR per-key mapping write)
_L3_USER_WRITE = re.compile(
    r"(?:\b\w*\.\s*\w*(?:share|balance|amount|stake|deposit)\w*|"
    r"\b\w*(?:share|balance|stake|deposit)s?\s*\[[^\]]+\])\s*(?:\+=|-=|=)(?!=)", re.I)
# a first-depositor / zero-supply branch guarding around a total/supply/shares quantity
_L3_ZERO_BRANCH = re.compile(r"\b(?:existing\w*|_)?(?:total\w*|\w*supply|\w*shares)\s*(?:!=|==)\s*0\b", re.I)
# a multiplicative ratio (global * share / total or total / global * share) — the reward-share computation
_L3_RATIO = re.compile(r"\*[^;{}]*/|/[^;{}]*\*")

# advisory contract — hard-stamped on every record
_STAMP = {"is_gate": False, "research_only": True, "emits_findings": False, "routes_in_production": False,
          "routed_manifest_ids": [], "severity": None, "reportable": False, "submission_ready": False,
          "concluded": False, "production_routing": False}


def _body(item: dict, audit_id) -> str | None:
    if not item:
        return None
    bd = _ssx.extract_body(item, audit_id)
    if bd.get("body_available") and not bd.get("is_declaration_only"):
        return bd.get("body")
    return None


def _contract_functions(manifest: dict, contract: str) -> list:
    return [i for i in manifest.get("items", [])
            if i.get("kind") == "function" and (i.get("contract") or "") == contract]


def _kin(name_a: str, name_b: str) -> bool:
    """cheap pre-filter so we only fetch bodies for plausible siblings (stem/core kinship)."""
    if not name_a or not name_b or name_a == name_b:
        return False
    return (_sfp._stem(name_a) == _sfp._stem(name_b)
            or (_sfp._core(name_a) == _sfp._core(name_b) and len(_sfp._core(name_a)) >= 4))


def _empty(status: str, reason: str) -> dict:
    return dict(_STAMP, invariant_delta_status=status, derivation_type=None, reference_basis=None,
                observed_expression_or_flow=None, expected_expression_or_flow=None, delta_hypothesis=None,
                affected_variables=[], attacker_influence_link=None, victim_gainer=None, poc_assertion=None,
                confidence="LOW", source_basis=reason, unresolved_assumptions=[reason])


# ---- D4.3 sibling-function reference (precision spine) ----
def _d43_sibling(item, manifest, audit_id, body):
    contract = item.get("contract") or ""
    cand_feat = _sfp.extract_features(item.get("name", ""), item.get("signature", ""),
                                      item.get("modifiers"), body or "", item.get("visibility", ""))
    sibs = [s for s in _contract_functions(manifest, contract)
            if s.get("name") != item.get("name") and _kin(item.get("name", ""), s.get("name", ""))][:MAX_SIB]
    hits = []
    for s in sibs:
        sbody = _body(s, audit_id)
        if not sbody:
            continue
        sfeat = _sfp.extract_features(s.get("name", ""), s.get("signature", ""), s.get("modifiers"),
                                      sbody, s.get("visibility", ""))
        for cand in _sfp.classify_pair(cand_feat, sfeat):
            # the candidate must be the WEAK side (the one missing the controlled component)
            if cand.get("weak") == item.get("name") and str(cand.get("confidence")).lower() in SIB_LIFT_CONF:
                hits.append(cand)
    if not hits:
        return None
    # ambiguity: conflicting missing components across distinct strong siblings -> fail closed
    comps = {h["missing_component"] for h in hits}
    if len(comps) > 1:
        rec = _empty("AMBIGUOUS_REFERENCE", "multiple conflicting sibling references")
        rec["affected_variables"] = sorted(comps)[:6]
        return rec
    h = sorted(hits, key=lambda c: 0 if str(c["confidence"]).lower() == "high" else 1)[0]
    conf = "HIGH" if str(h["confidence"]).lower() == "high" else "MEDIUM"
    return dict(_STAMP, invariant_delta_status="SIBLING_REFERENCE_FOUND", derivation_type="D4.3_sibling_reference",
                reference_basis=f"sibling {h['strong']} ({h['parity_type']})",
                observed_expression_or_flow=f"{h['weak']} omits {h['missing_component']} on a shared mutating path",
                expected_expression_or_flow=f"apply {h['missing_component']} as sibling {h['strong']} does",
                delta_hypothesis=f"{h['weak']} diverges from {h['strong']}: missing {h['missing_component']} "
                                 f"({h['parity_type']})",
                affected_variables=[h["missing_component"]],
                attacker_influence_link=f"permissionless call to {h['weak']} reaches the divergent path",
                victim_gainer="stakeholder of the omitted component (recipient/guarded state)",
                poc_assertion=f"assert {h['weak']} result differs from the {h['strong']} reference because "
                              f"{h['missing_component']} is not applied",
                confidence=conf, source_basis=h.get("evidence", ""),
                unresolved_assumptions=[] if conf == "HIGH" else ["sibling kinship is behavioral, not name-stem"])


# ---- D4.2 symmetric ledger / registry desync (precision spine) ----
def _d42_registry(item, manifest, audit_id):
    contract = item.get("contract") or ""
    feats = []
    for f in _contract_functions(manifest, contract):
        fb = _body(f, audit_id)
        feats.append(_rpl.extract_registry_features(f.get("name", ""), f.get("signature", ""), fb or "",
                                                    f.get("visibility", ""), f.get("mutability", "")))
    if not feats:
        return None
    for cand in _rpl.classify_contract(feats, contract):
        weak = cand.get("function")
        if weak == item.get("name"):
            strong = cand.get("sibling_updater")
            conf = "HIGH" if str(cand.get("confidence")).lower() == "high" else "MEDIUM"
            return dict(_STAMP, invariant_delta_status="CONSERVATION_FOUND",
                        derivation_type="D4.2_symmetric_ledger",
                        reference_basis=f"registry/lifecycle sibling {strong} ({cand.get('shape')})",
                        observed_expression_or_flow=cand.get("evidence", f"{weak} omits a symmetric ledger update"),
                        expected_expression_or_flow=cand.get("missing_component", "the symmetric position/global update"),
                        delta_hypothesis=f"{weak}: {cand.get('shape', 'registry/position desync')}",
                        affected_variables=[cand.get("missing_component", "registry update")],
                        attacker_influence_link=f"permissionless call to {weak} desyncs position vs global ledger",
                        victim_gainer="protocol accounting / other positions",
                        poc_assertion=f"assert position and global ledger desync after {weak} "
                                      f"(missing {cand.get('missing_component', 'symmetric update')})",
                        confidence=conf, source_basis=cand.get("evidence", ""),
                        unresolved_assumptions=[])
    return None


# ---- D4.4 corrected-reference: computed-not-applied / rounding-direction ----
def _d44_corrected(item, body):
    b = _ssx.strip_comments(body)
    # rounding-direction evidence (bound_semantics pure helper) for share/precision math
    for term in ("floor", "ceil", "round", "muldiv"):
        ok, why = _bsg._rounding_evidence(term, b)
        if ok and ("/" in b and "*" in b):
            return dict(_STAMP, invariant_delta_status="REFERENCE_FOUND", derivation_type="D4.4_rounding_direction",
                        reference_basis=f"rounding-direction evidence ({term})",
                        observed_expression_or_flow=why, expected_expression_or_flow="opposite rounding direction "
                        "for the protocol-favoring side",
                        delta_hypothesis=f"rounding direction ({term}) may favor the caller over the protocol",
                        affected_variables=[term], attacker_influence_link="caller benefits from the rounding bias",
                        victim_gainer="protocol reserve / other users", poc_assertion="assert rounding favors caller "
                        "vs the protocol-favoring reference direction", confidence="MEDIUM", source_basis=why,
                        unresolved_assumptions=["rounding bias direction must be confirmed against intended side"])
    return None


# ---- D4.1 / D4.5 conservation & before/after equation (local bounded-SSA; assertion only, not a lift on its own) ----
def _d15_equation(item, body):
    b = _ssx.strip_comments(body)
    bl = b.lower()
    bal = _BAL.findall(bl)
    totals = sorted(set(_TOTAL.findall(b)))
    has_before_after = (bl.count("balanceof") >= 2) or any("before" in x for x in bal) and any("after" in x for x in bal)
    if has_before_after:
        return ("balanceAfter - balanceBefore == expectedReceived", ["balanceBefore", "balanceAfter"], "before/after")
    if totals:
        return (f"{totals[0]}After - {totals[0]}Before == minted/burned amount", totals[:2], "conservation")
    return None


# ---- D4.6 oracle normalization ----
def _d46_oracle(item, body):
    b = _ssx.strip_comments(body).lower()
    if not any(m in b for m in ("latestrounddata", "latestanswer", "getprice", "oracle", "twap")):
        return None
    used_in_value = any(t in b for t in ("collateral", "debt", "value", "price", "amount", "shares"))
    has_norm = any(m in b for m in ORACLE_NORM)
    has_stale = any(m in b for m in ORACLE_STALE)
    if used_in_value and not (has_norm and has_stale):
        missing = ("decimals normalization" if not has_norm else "") + (
            " + staleness check" if not has_stale else "")
        return dict(_STAMP, invariant_delta_status="REFERENCE_FOUND", derivation_type="D4.6_oracle_normalization",
                    reference_basis="oracle read feeding a value computation",
                    observed_expression_or_flow="price/oracle value used in valuation without " + missing.strip(),
                    expected_expression_or_flow="apply feed-decimals scaling and staleness check before valuation",
                    delta_hypothesis=f"oracle value enters collateral/debt/value path missing {missing.strip()}",
                    affected_variables=["oracle price"], attacker_influence_link="attacker times stale/unnormalized "
                    "price to mis-value", victim_gainer="protocol solvency / counterparties",
                    poc_assertion="assert valuation uses an unnormalized/stale price vs the normalized reference",
                    confidence="MEDIUM" if (not has_norm and not has_stale) else "LOW",
                    source_basis="oracle markers present; normalization/staleness markers absent",
                    unresolved_assumptions=["normalization/staleness may occur in a helper not in this span"])
    return None


# ---- D4.7 state-machine value invariant (reuse P281 evidence) ----
def _d47_state(item, gate_evidence, award_class):
    ge = gate_evidence or {}
    if award_class in STATE_CLASSES and ge.get("state_machine_detected") and ge.get("or_state_gate"):
        return dict(_STAMP, invariant_delta_status="STATE_MACHINE_DELTA_FOUND",
                    derivation_type="D4.7_state_machine_value_invariant",
                    reference_basis="state-machine gate accepts a forbidden state (or-state)",
                    observed_expression_or_flow="value/state mutation reachable in a forbidden lifecycle state",
                    expected_expression_or_flow="mutation gated to the single permitted state",
                    delta_hypothesis="or-state gate admits a forbidden state into the value/state mutation",
                    affected_variables=ge.get("state_markers", []),
                    attacker_influence_link="permissionless call in the forbidden state",
                    victim_gainer="protocol governance / protected state",
                    poc_assertion="assert the mutation succeeds in a forbidden state it should reject",
                    confidence="MEDIUM", source_basis=f"P281 state-machine evidence at {ge.get('source_span')}",
                    unresolved_assumptions=[])
    return None


# ---- P289 loss/reward mechanism lenses (generic; multi-signal; MEDIUM ceiling; fail-closed) ----
def _lens_rec(status, lens_name, lens_status, **kw):
    base = dict(_STAMP, invariant_delta_status=status, lens_name=lens_name, lens_status=lens_status,
                derivation_type=f"P289_{lens_name}", confidence="MEDIUM", unresolved_assumptions=[])
    base.update(kw)
    return base


def _name_or_body(item, b, terms):
    nm = (item.get("name") or "").lower()
    return any(t in nm for t in terms) or any(t in b for t in terms)


def _lens_loss_on_stake(item, body):
    b = _ssx.strip_comments(body).lower()
    stake = _name_or_body(item, b, L_STAKE)
    loss = any(t in b for t in L_LOSS)
    user_write = any(m in b for m in L_UWRITE)
    index = any(t in b for t in L_INDEX)
    if not (stake and loss and user_write):
        return None
    # incomplete-guard variant: a same-block-only loss guard protects only same-block, not prior-block loss
    sameblock_loss_guard = bool(_SAMEBLOCK_GUARD.search(b)) and loss
    # init present: a user index/checkpoint is assigned (incl. indexed `userIndex[k] = ...` or struct `profitIndex: ...`)
    # from an index/per-token/accumulator getter call in this body
    init_present = index and bool(re.search(
        r"(?:index|checkpoint)\w*(?:\[[^\]]*\])?\s*[:=]\s*[^;,}]*(?:index|pertoken|accumulator)\s*\(", b))
    if init_present and not sameblock_loss_guard:
        return _lens_rec("NO_REFERENCE", "loss_on_stake", "LENS_REFUTED",
                         refutation_basis="user index initialized to current global on stake; no same-block-only narrowing",
                         source_basis="stake writes user index from a current-global getter",
                         confidence="LOW")
    return _lens_rec("LOSS_ON_STAKE_FOUND", "loss_on_stake", "LENS_MATCH",
                     reference_basis="prior loss/slash state coupled into a new stake",
                     observed_expression_or_flow="new stake records/incurs loss state with " +
                     ("only a same-block loss guard" if sameblock_loss_guard else "no prior-loss exclusion"),
                     expected_expression_or_flow="exclude prior-block loss from a new stake (init checkpoint AND guard "
                     "prior losses, not only same-block)",
                     delta_hypothesis="a staker can be slashed for / inherit a pre-existing (prior-block) loss",
                     affected_variables=["user stake/share", "loss/profit index"],
                     attacker_influence_link="actor stakes after a loss/deficit exists in the same gauge/term",
                     victim_gainer="new staker loses value; existing deficit is subsidized",
                     poc_assertion="stake after a seeded prior-block loss; assert the new position is slashed / valued "
                     "below an initialized-checkpoint control",
                     source_basis="stake verb + loss/slash state + per-user write" +
                     (" + same-block-only guard" if sameblock_loss_guard else ""),
                     unresolved_assumptions=([] if sameblock_loss_guard else
                                             ["prior-loss exclusion may exist in a helper not in this span"]))


def _lens_bad_debt_contagion(item, body):
    b = _ssx.strip_comments(body).lower()
    loss_evt = _name_or_body(item, b, L_LOSS_EVT)
    loss = any(t in b for t in L_LOSS)
    # a write to a global/shared accumulator on the loss path
    global_write = bool(re.search(r"\b\w*(?:total|global|shared|cumulative|buffer)\w*\s*(?:\+=|-=|=)\s*[^=]", b))
    per_keyed = any(k in b for k in L_PERKEY)
    if not (loss_evt and loss):
        return None
    if per_keyed and not global_write:
        return _lens_rec("NO_REFERENCE", "bad_debt_contagion", "LENS_REFUTED",
                         refutation_basis="loss writes are per-term/user keyed (isolated)", confidence="LOW")
    if not global_write:
        return None  # no global/shared loss write -> no contagion signal
    return _lens_rec("BAD_DEBT_CONTAGION_FOUND", "bad_debt_contagion", "LENS_MATCH",
                     reference_basis="loss event writes a global/shared accumulator",
                     observed_expression_or_flow="a liquidation/bid/writeoff loss is written to global/shared state",
                     expected_expression_or_flow="isolate loss to the affected term/position unless shared-risk is "
                     "explicit",
                     delta_hypothesis="loss from one position/term propagates to unrelated positions via shared state",
                     affected_variables=["global loss/debt accumulator", "unrelated user/term balances"],
                     attacker_influence_link="attacker triggers a loss event (bid/liquidation/writeoff) on one position",
                     victim_gainer="unrelated stakers/lenders absorb the loss; bad-debt actor/deficit benefits",
                     poc_assertion="create a loss in position A; assert an unrelated position B's balance/index/capacity "
                     "changes",
                     source_basis="loss-event verb + loss term + global/shared accumulator write",
                     unresolved_assumptions=(["shared-risk pool may be intended design"] if per_keyed else []))


def _lens_reward_index_init(item, body):
    b = _ssx.strip_comments(body).lower()
    global_idx = any(t in b for t in ("rewardindex", "globalindex", "rewardpertoken", "accumulator", "gaugeprofitindex"))
    user_idx = any(t in b for t in ("userindex", "userrewardpertokenpaid", "usercheckpoint", "profitindex"))
    bal_write = any(m in b for m in L_UWRITE) or any(t in b for t in L_STAKE)
    reward_path = any(t in b for t in L_REWARD)
    if not (global_idx and user_idx and bal_write and reward_path):
        return None
    # atomic init: user index assigned from a current-global read in this body
    atomic_init = bool(re.search(r"(userindex|userrewardpertokenpaid|usercheckpoint|profitindex)\s*[:=][^;]*"
                                 r"(index|pertoken|accumulator)\s*\(?", b))
    if atomic_init:
        return _lens_rec("NO_REFERENCE", "reward_index_init", "LENS_REFUTED",
                         refutation_basis="user index initialized atomically with the balance change", confidence="LOW")
    return _lens_rec("REWARD_INDEX_INIT_FOUND", "reward_index_init", "LENS_MATCH",
                     reference_basis="user reward index not initialized on balance change",
                     observed_expression_or_flow="user balance becomes positive without its reward index set to current",
                     expected_expression_or_flow="initialize user index to the current global index on first balance",
                     delta_hypothesis="stale/zero user index lets the user reap retroactive rewards or escape losses",
                     affected_variables=["user balance/share", "user reward index/checkpoint"],
                     attacker_influence_link="user acquires balance after the global index moved, then claims/accrues",
                     victim_gainer="attacker gains unearned rewards / victim absorbs prior losses",
                     poc_assertion="move global index, create user balance, claim/accrue; compare to an "
                     "initialized-control path",
                     source_basis="global index + user index + balance write + claim path; no atomic user-index init",
                     unresolved_assumptions=["user-index init may occur in a helper resolved by trace"])


# ---- P293 cross-function, naming-flexible reward-index lens (Lens 3) ----
def _l3_hits(text, terms):
    return sorted({t for t in terms if t in text})


def _l3_pending_in(union, user_index_terms):
    """A pending-reward formula in the assembled spans: a multiplicative reward-share ratio."""
    if not _L3_RATIO.search(union):
        return None
    has_snap = any(u in union for u in user_index_terms)
    return {"basis": "reward-share ratio in-span" + (" minus user snapshot" if has_snap else " (no per-user debt term)"),
            "consumes_snapshot": has_snap}


def _l3_sibling_pending(item, manifest, audit_id, user_index_terms, contract):
    """Same-contract sibling view/claim that computes a reward-share ratio consuming a user snapshot var."""
    cnt = 0
    for f in _contract_functions(manifest, contract):
        if cnt >= L3_MAX_SIB:
            break
        if f.get("name") == item.get("name"):
            continue
        nm = (f.get("name") or "").lower()
        if not (any(p in nm for p in L3_PENDING) or "reward" in nm):
            continue
        cnt += 1
        fb = _body(f, audit_id)
        if not fb:
            continue
        t = _ssx.strip_comments(fb).lower()
        if _L3_RATIO.search(t) and any(u in t for u in user_index_terms):
            return {"sibling": f.get("name"), "basis": f"pending formula in sibling {f.get('name')} "
                    "(reward-share ratio minus user snapshot)", "consumes_snapshot": True}
    return None


def _l3_share_before_checkpoint(root):
    """True iff a per-user share write precedes the first reward checkpoint/update marker (B: checkpoint-after-share)."""
    m = _L3_USER_WRITE.search(root)
    if not m:
        return False
    cps = [root.find(k) for k in ("updatereward", "_updatereward", "accrue", "checkpoint")]
    cps = [i for i in cps if i >= 0]
    return bool(cps) and min(cps) > m.start()


def _l3_record(lens3_status, lens3_pattern, **kw):
    """A Lens-3 result; lifts only when lens3_status == LENS3_READY (-> REWARD_INDEX_INIT_FOUND)."""
    lift = lens3_status == "LENS3_READY"
    base = dict(_STAMP,
                invariant_delta_status=("REWARD_INDEX_INIT_FOUND" if lift else "NO_REFERENCE"),
                lens_name="reward_index_cross", lens_status=("LENS_MATCH" if lift else "LENS_HELD"),
                derivation_type="P293_reward_index_cross",
                lens3_status=lens3_status, lens3_pattern=lens3_pattern,
                confidence=("MEDIUM" if lift else "LOW"), unresolved_assumptions=[])
    base.update(kw)
    return base


def _lens_reward_index_cross(item, body, manifest=None, audit_id=None, trace_evidence=None):
    """Naming-flexible, cross-function reward-index lens (P293).

    First preserves the P289 span-local `_lens_reward_index_init` behavior byte-for-byte (so its fixtures/lifts are
    unchanged). When span-local finds nothing, assembles the union of the candidate body + already-resolved P283
    trace callees + a same-contract pending-formula sibling, applies broadened (config) name families, and lifts ONLY
    on a source-backed reward-debt/first-depositor deviation with a connectable pending formula. Fail-closed otherwise.
    """
    # 1) span-local P289 path (unchanged behavior) — enrich with lens3 fields, never weaken
    span = _lens_reward_index_init(item, body)
    if span is not None:
        span = dict(span)
        refuted = span.get("lens_status") == "LENS_REFUTED"
        span["lens3_status"] = "LENS3_REFUTED_NORMAL_CHECKPOINT" if refuted else "LENS3_READY"
        span["lens3_pattern"] = "MISSING_USER_INDEX_INIT"
        span["trace_path_used"] = []
        return span
    if manifest is None:
        return None

    # 2) cross-function naming-flexible detection
    contract = item.get("contract") or ""
    root = _ssx.strip_comments(body).lower()
    spans = [("__root__", root)]
    trace_used = []
    te = trace_evidence or {}
    tstatus = te.get("trace_status")
    had_unresolved = bool(te.get("unresolved_callees"))
    if tstatus and tstatus != "TRACE_UNRESOLVED":
        idx = build_index(manifest)
        for edge in (te.get("trace_path") or [])[:L3_MAX_SIB]:
            cal = idx.get(edge.get("callee"))
            if not cal:
                continue
            cb = _body(cal, audit_id)
            if cb:
                spans.append((edge.get("callee"), _ssx.strip_comments(cb).lower()))
                trace_used.append(edge.get("callee"))
    union = "\n".join(s for _, s in spans)

    user_share_write = bool(_L3_USER_WRITE.search(union))
    global_index = _l3_hits(union, L3_GLOBAL_INDEX)
    user_index = _l3_hits(union, L3_USER_INDEX)
    loss_vars = _l3_hits(union, L3_LOSS)
    share_vars = _l3_hits(union, L3_USER_SHARE) + _l3_hits(union, L3_GLOBAL_SHARE)
    zero_branch = bool(_L3_ZERO_BRANCH.search(union))

    # relevance gate: must look like reward/index accounting at all, else stay silent (derive() unchanged elsewhere)
    if not (user_share_write and (global_index or user_index or loss_vars)):
        return None

    # pending-reward formula (in-span OR a same-contract sibling consuming a user snapshot)
    pending = _l3_pending_in(union, user_index) or (
        _l3_sibling_pending(item, manifest, audit_id, user_index, contract) if user_index else None)

    # refutation: a proper checkpoint protects the path — either (a) the user snapshot is assigned from a current
    # global read (atomic init), or (b) a checkpoint/updateReward CALL precedes the share mutation (checkpoint-then-
    # mutate, the canonical Synthetix-correct ordering). A conditionally-skipped snapshot (zero_branch) is NOT refuted.
    root_only = "\n".join(s for k, s in spans if k == "__root__")
    atomic = False
    if user_index and global_index:
        atomic = bool(re.search(
            r"(?:" + "|".join(map(re.escape, user_index)) + r")\w*\s*(?:\[[^\]]*\])?\s*=\s*[^;]*(?:"
            + "|".join(map(re.escape, global_index)) + r")", union))
    cp_call = bool(re.search(r"\b(?:updatereward|_updatereward|accrue|checkpoint)\s*\(", root_only))
    checkpoint_before_share = cp_call and not _l3_share_before_checkpoint(root_only)
    if (atomic or checkpoint_before_share) and not zero_branch:
        return _l3_record("LENS3_REFUTED_NORMAL_CHECKPOINT", None,
                          source_basis=("user snapshot initialized from the current global index (atomic checkpoint)"
                                        if atomic else "reward checkpoint/update precedes the share mutation"),
                          global_index_vars=global_index, user_index_vars=user_index, share_vars=share_vars,
                          trace_path_used=trace_used)

    fields = dict(global_index_vars=global_index, user_index_vars=user_index, share_vars=share_vars,
                  trace_path_used=trace_used,
                  pending_reward_formula_basis=(pending.get("basis") if pending else None))

    # ---- Pattern E (loss/reward contagion): a global/shared loss accumulator coupled into a share mutation with no
    #      per-user snapshot to exclude prior loss. Checked first; the loss propagation is itself the basis (no pending
    #      formula required). Requires a GLOBAL/shared loss accumulator to avoid matching benign per-position loss. ----
    pattern = impact = None
    global_loss = bool(re.search(r"\b\w*(?:total|global|shared|gauge|cumulative)\w*loss\w*", union))
    if loss_vars and global_loss and not (user_index and pending and pending.get("consumes_snapshot")):
        pattern = "LOSS_REWARD_INDEX_CONTAGION"
        impact = "a new staker inherits a pre-existing global/shared loss delta (no per-user snapshot excludes it)"

    if pattern is None:
        # ---- gates apply to the reward-index patterns A/B/C/D (not the loss-contagion fast path) ----
        if not global_index:
            st = "LENS3_TRACE_UNRESOLVED" if (had_unresolved and not trace_used) else "LENS3_NO_GLOBAL_INDEX"
            return _l3_record(st, None,
                              source_basis="user share mutation present; no global index/accumulator reachable"
                              + (" (callees unresolved)" if st == "LENS3_TRACE_UNRESOLVED" else ""),
                              unresolved_assumptions=(["global index/accumulator may live in an unresolved callee"]
                                                      if st == "LENS3_TRACE_UNRESOLVED" else []), **fields)
        if not pending:
            return _l3_record("LENS3_PATTERN_MATCH_HELD", None,
                              source_basis="reward/index accounting present but no connectable pending/claim formula",
                              unresolved_assumptions=["pending/claim formula not found in span/callees/siblings"],
                              **fields)
        if user_index and zero_branch:
            pattern = "FIRST_DEPOSITOR_ZERO_SUPPLY"
            impact = ("the per-user reward snapshot is skipped on the zero-supply/first-depositor branch, so the first "
                      "depositor's claimable diverges from a checkpointed reference")
        elif not user_index:
            pattern = "MISSING_USER_INDEX_INIT"
            impact = "user share is created without a per-user reward snapshot, so the user reaps the global reward delta"
        elif _l3_share_before_checkpoint("\n".join(s for k, s in spans if k == "__root__")):
            pattern = "SHARE_INCREASE_BEFORE_CHECKPOINT"
            impact = ("the user's reward checkpoint is updated after (or without) the share increase, so a new/changed "
                      "position inherits past reward accrual")
        elif not atomic:
            pattern = "GLOBAL_INDEX_NOT_PAIRED"
            impact = ("the global accumulator and user share move without a paired, current user-index update, so the "
                      "pending formula (global-minus-user) mis-accounts rewards")
        else:
            return _l3_record("LENS3_NO_ORDERING_EVIDENCE", None,
                              source_basis="snapshot present and paired; no missing-init/ordering/zero-supply deviation",
                              **fields)

    snapshot_basis = ("snapshot write conditionally skipped on a zero-supply branch" if zero_branch else
                      "no per-user snapshot write on the share-mutation path" if not user_index else
                      "global loss/index coupled into the position without a per-user exclusion"
                      if pattern == "LOSS_REWARD_INDEX_CONTAGION" else
                      "global index moves without a paired current user-index update")
    return _l3_record(
        "LENS3_READY", pattern,
        reference_basis="reward-debt / index accounting compared against a correct-checkpoint reference",
        observed_expression_or_flow="user share mutates while the per-user reward snapshot is missing/stale/"
        "conditionally-skipped relative to the global accumulator",
        expected_expression_or_flow="initialize/checkpoint the per-user reward index to the current global index "
        "atomically with every share mutation",
        delta_hypothesis=impact,
        affected_variables=(share_vars + global_index + user_index)[:8],
        attacker_influence_link="actor permissionlessly mutates share after the global index/reward moved, then claims",
        victim_gainer="attacker captures unearned reward / avoids loss; honest stakers are diluted",
        ordering_evidence=("zero-supply branch guards the snapshot write" if zero_branch else
                           "share mutation without paired user-index update"),
        missing_or_incorrect_snapshot_basis=snapshot_basis,
        impact_delta=impact,
        poc_assertion="seed the global reward/index, perform the share mutation, then claim/withdraw; assert the "
        "claimable/owed diverges from a control path that checkpoints the user index atomically",
        source_basis=f"share mutation + global index {global_index or 'loss-accumulator'} + user snapshot "
        f"{user_index or 'MISSING'} + pending formula ({pending.get('basis') if pending else 'loss propagation'})"
        + (f"; trace callees {trace_used}" if trace_used else ""),
        confidence="MEDIUM", unresolved_assumptions=[], **fields)


def _lens_share_transfer_theft(item, body):
    b = _ssx.strip_comments(body).lower()
    is_transfer = any(m in b for m in L_XFER) or (item.get("name") or "").lower() in ("transfer", "transferfrom")
    share = any(t in b for t in L_SHARE)
    reward = any(t in b for t in ("reward", "index", "checkpoint", "accumulator", "earned", "rebasing"))
    if not (is_transfer and share and reward):
        return None
    # both-side checkpoint update present? (sender AND recipient state both touched)
    from_to = (("from" in b or "msg.sender" in b) and ("to" in b)
               and len(re.findall(r"(checkpoint|index|rewarddebt|nshares|rebasingstate)", b)) >= 2)
    if from_to:
        return _lens_rec("NO_REFERENCE", "share_transfer_theft", "LENS_REFUTED",
                         refutation_basis="transfer updates both sender and recipient reward checkpoints/shares",
                         confidence="LOW")
    return _lens_rec("SHARE_TRANSFER_THEFT_FOUND", "share_transfer_theft", "LENS_MATCH",
                     reference_basis="balance-dependent reward path without a from/to checkpoint update on transfer",
                     observed_expression_or_flow="shares/balance transfer affects reward entitlement without "
                     "checkpointing sender/recipient",
                     expected_expression_or_flow="update both sender and recipient reward checkpoints around transfer",
                     delta_hypothesis="rewards are stolen/duplicated/lost because transfer skips reward checkpointing",
                     affected_variables=["sender/recipient balance", "reward index/claimable"],
                     attacker_influence_link="attacker transfers shares around reward-index movement then claims",
                     victim_gainer="wrong party claims rewards / victim loses accrued rewards",
                     poc_assertion="accrue rewards, transfer shares, claim; compare claimant/amount to a "
                     "checkpointed-control reference",
                     source_basis="transfer + shares/balance + reward/index path; no both-side checkpoint update",
                     unresolved_assumptions=["a transfer hook may checkpoint in a helper not in this span"])


def derive(item: dict, manifest: dict, audit_id=None, gate_evidence: dict | None = None,
           trace_evidence: dict | None = None) -> dict:
    """Consolidated invariant-delta derivation for one candidate. Returns the strongest source-backed record."""
    award_class = item.get("award_class") or (item.get("tags") or [None])[0]
    body = _body(item, audit_id)
    if body is None:
        return _empty("INSUFFICIENT_SOURCE", "no resolvable function body / declaration-only")

    # D4.7 (state class) first — independent of value classes
    st = _d47_state(item, gate_evidence, award_class)
    # precision-spine deviation detectors (D4.2 / D4.3 / D4.4 / D4.6)
    found = []
    for fn in (lambda: _d43_sibling(item, manifest, audit_id, body),
               lambda: _d42_registry(item, manifest, audit_id),
               lambda: _d44_corrected(item, body),
               lambda: _d46_oracle(item, body),
               # P289 loss/reward mechanism lenses
               lambda: _lens_loss_on_stake(item, body),
               lambda: _lens_bad_debt_contagion(item, body),
               lambda: _lens_reward_index_cross(item, body, manifest, audit_id, trace_evidence),
               lambda: _lens_share_transfer_theft(item, body)):
        try:
            r = fn()
        except Exception:
            r = None
        if r:
            found.append(r)
    if st:
        found.append(st)

    # ambiguity short-circuit (sibling)
    amb = next((r for r in found if r["invariant_delta_status"] == "AMBIGUOUS_REFERENCE"), None)
    real = [r for r in found if r["invariant_delta_status"] in LIFT_STATUSES]
    if not real:
        if amb:
            return amb
        # no deviation reference; record what local material exists (equation = assertion scaffolding only)
        eq = _d15_equation(item, body)
        base = _empty("NO_REFERENCE", "no source-backed deviation reference found")
        if eq:
            base["poc_assertion"] = eq[0]
            base["affected_variables"] = eq[1]
            base["source_basis"] = f"local {eq[2]} equation extracted (assertion scaffold only; no deviation)"
            base["unresolved_assumptions"] = ["before/after equation present but no deviation detector corroborates"]
        # P293: surface a precise Lens-3 block reason when the reward-index lens matched a pattern but held
        held = next((r for r in found if r.get("lens_name") == "reward_index_cross" and r.get("lens3_status")), None)
        if held:
            for k in ("lens3_status", "lens3_pattern", "global_index_vars", "user_index_vars", "share_vars",
                      "trace_path_used", "pending_reward_formula_basis"):
                if k in held:
                    base[k] = held[k]
            base["source_basis"] = held.get("source_basis") or base["source_basis"]
        return base

    # strongest deviation wins; HIGH over MEDIUM
    real.sort(key=lambda r: 0 if r["confidence"] == "HIGH" else 1)
    best = real[0]
    # enrich the lift record with a concrete before/after assertion when available
    eq = _d15_equation(item, body)
    if eq and (not best.get("poc_assertion") or best["invariant_delta_status"] in ("CONSERVATION_FOUND",)):
        best = dict(best)
        best["poc_assertion"] = best.get("poc_assertion") or eq[0]
        if best["invariant_delta_status"] == "CONSERVATION_FOUND":
            best["invariant_delta_status"] = "DELTA_FOUND"  # deviation + concrete equation
            best["observed_expression_or_flow"] = (best.get("observed_expression_or_flow") or "") + f"; {eq[0]}"
    return best


def build_index(manifest: dict) -> dict:
    return {f"{i.get('contract')}.{i.get('name')}": i
            for i in manifest.get("items", []) if i.get("kind") == "function"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--contract-function", required=True)
    ap.add_argument("--audit-id")
    a = ap.parse_args()
    man = json.loads(Path(a.manifest).read_text())
    c, _, fn = a.contract_function.partition(".")
    item = next((i for i in man.get("items", []) if i.get("kind") == "function" and i.get("name") == fn
                 and c in (i.get("contract") or "")), None)
    ge = None
    if item:
        try:
            ge = _ssx.extract(item, a.audit_id)
        except Exception:
            ge = None
    print(json.dumps(derive(item or {}, man, a.audit_id, ge, None), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
