#!/usr/bin/env python3
"""
adjudication_rubric.py — RESEARCH-ONLY mechanism validity/severity adjudication rubric (P187). UN-WIRED.

P186 showed deep-pass mechanism *enumeration* is model-robust, but *adjudication* (is an enumerated mechanism a
real, in-severity bug?) is model-sensitive: Sonnet rejected M-02 and M-06 with confident source-backed reasons
that the P185 `demoted_unresolved_mechanism` checker does not flag. This module encodes an OBJECTIVE rubric that,
given an enumerated mechanism + its source evidence + a model's disposition, decides one of five outcomes and —
crucially — names the evidence that would SETTLE a disagreement, instead of picking a model.

The rubric (9 checks, see VALIDITY_RUBRIC.md):
  1 units consistency · 2 value-direction · 3 who-gains/who-loses · 4 exploit preconditions ·
  5 attacker controllability · 6 invariant violation · 7 severity boundary (lowest tier the mechanism CLEARS) ·
  8 rejection responsiveness (does the rejecting fact address the ALLEGED failure mode + locus, on a proven fact?) ·
  9 settling evidence (is a minimal corrected-reference / differential check feasible?)
Outcomes: SELECTED_VALID · SELECTED_NEEDS_HARNESS · UNRESOLVED_CARRY_FORWARD · REJECTED_VALIDLY · REJECTED_INCORRECTLY.

The two functions that close the P186 checker gap are `rejection_is_responsive` (#8 — locus + failure-mode match)
and `applies_too_high_severity_bar` (#7 — a fund-loss/High bar applied to a finding that clears a lower tier).

RESEARCH DETECTOR PLATFORM DISCIPLINE (CLAUDE.md): this file carries research_only=true /
routes_in_production=false / is_gate=false, is imported by NOTHING in production (no run_pipeline / agent_policy /
coverage_sweep / dependency_clear / *_audit reference), is READ-ONLY (reads frozen P186 artifacts + the answer
key; writes one research matrix under documentation/research/), and NEVER mints findings, sets severity, routes,
gates, or mutates dispositions/corpus/answer-key. It does not adjudicate production findings — it scores frozen
evidence to calibrate a future, separately-approved prompt/checker change. Promotion is a later human decision.

Usage: python scripts/research/adjudication_rubric.py            # emits adjudication_matrix.json
"""
from __future__ import annotations

import json
from pathlib import Path

_FLAGS = {"research_only": True, "routes_in_production": False, "is_gate": False, "re_surface_only": True}
ROOT = Path(__file__).resolve().parent.parent.parent
P186 = ROOT / "documentation/research/assisted_mode/p186_fresh_model_blind_selection"
P187 = ROOT / "documentation/research/assisted_mode/p187_adjudication_calibration"
ANSWER_KEY = ROOT / "audits/quantamm-2024-12-eval/output/answer_key/normalized_answer_key.json"

# Outcome constants (the five the spec names).
SELECTED_VALID = "SELECTED_VALID"
SELECTED_NEEDS_HARNESS = "SELECTED_NEEDS_HARNESS"
UNRESOLVED_CARRY_FORWARD = "UNRESOLVED_CARRY_FORWARD"
REJECTED_VALIDLY = "REJECTED_VALIDLY"
REJECTED_INCORRECTLY = "REJECTED_INCORRECTLY"

# Severity tiers, lowest→highest (CLAUDE.md scale). A DoS clears Medium; a fund-loss path clears High/Critical.
_TIER_RANK = {"Info": 0, "Low": 1, "Medium": 2, "High": 3, "Critical": 4}

# Failure-mode families — used to classify BOTH the alleged bug (from its description) and a model's rejecting
# fact (from its own words), so responsiveness (#8) is computed from text, not asserted.
_FAMILY_KEYWORDS = {
    "UNITS": ("units", "1e18", "scale", "decimal", "dimension", "normaliz", "cancels"),
    "DIRECTION_UNDERFLOW": ("underflow", "subtraction", "negative", "truncat", "rounds to 0",
                            "rounds down to", "integer division", "value change", "valuechange"),
    "LIVENESS_DOS": ("revert", "dos", "denial", "lock", "liveness", "stale", "unavailable", "brick"),
    "AUTH": ("unauthor", "access control", "access-control", "spoof", "msg.sender", "delete", "identity"),
    "BOUND": ("exceed", "cap", "> 100", ">100", "bound", "limit", "100%", "no upper"),
    "PRECISION": ("precision", "truncat", "rounding", "floor-division", "sequential"),
    "TIMING_TYPE": ("block.number", "block.timestamp", "wrong type", "timestamp"),
}

# A rejection that invokes a HIGHER-than-claimed severity bar (the M-06 failure mode).
_HIGH_BAR_TOKENS = ("not fund-loss", "not fund loss", "fund-loss", "fund loss", "liveness/dos not",
                    "dos not fund", "view function", "not a fund", "no fund loss")


def families_of(text: str) -> set:
    """Classify a piece of text into failure-mode families by keyword. Pure, deterministic."""
    s = (text or "").lower()
    return {fam for fam, kws in _FAMILY_KEYWORDS.items() if any(k in s for k in kws)}


def rejection_is_responsive(rejecting_fact: str, alleged_locus_tokens, alleged_families: set,
                            leans_on_unproven_guard: bool) -> dict:
    """CHECK #8. A rejection is RESPONSIVE only if it (a) references the alleged bug's locus (the specific
    variable/expression), (b) addresses the alleged failure-mode family, and (c) does not lean on an unproven
    guard. A units-consistency rebuttal of an underflow claim, or a rebuttal aimed at a different expression, is
    NON-RESPONSIVE — the M-02 failure mode the P185 checker misses. Returns the booleans + verdict."""
    s = (rejecting_fact or "").lower()
    locus_ref = any(str(t).lower() in s for t in (alleged_locus_tokens or []))
    rej_families = families_of(rejecting_fact)
    family_match = bool(rej_families & alleged_families)
    responsive = bool(locus_ref and family_match and not leans_on_unproven_guard)
    return {"locus_referenced": locus_ref, "rejection_families": sorted(rej_families),
            "family_match": family_match, "leans_on_unproven_guard": bool(leans_on_unproven_guard),
            "responsive": responsive}


def applies_too_high_severity_bar(rejecting_fact: str, lowest_tier_cleared: str) -> bool:
    """CHECK #7. True when the rejection rebuts only a HIGHER tier than the mechanism needs to clear — e.g.
    rejecting a DoS (clears Medium) for not being fund-loss (a High/Critical bar). This is the M-06 failure mode."""
    invokes_high_bar = any(t in (rejecting_fact or "").lower() for t in _HIGH_BAR_TOKENS)
    return bool(invokes_high_bar and _TIER_RANK.get(lowest_tier_cleared, 9) <= _TIER_RANK["Medium"])


def adjudicate(case: dict) -> dict:
    """Apply the decision tree to one case. `case` carries the model disposition + the objective facts the checks
    need. Returns {outcome, reason, settling_check, harness_required, checks{...}}. Pure; never raises."""
    disp = case["model_disposition"]            # selected | unresolved | rejected
    alleged_families = families_of(case["alleged_failure_mode"])
    checks = {"alleged_families": sorted(alleged_families),
              "lowest_tier_cleared": case["lowest_tier_cleared"]}

    if disp == "selected":
        # Carried as a primary mechanism with a named who-loses → valid (severity is a calibration note, not a
        # rejection). No rubric check can demote a selected, impact-bearing mechanism here.
        checks["who_loses_named"] = bool(case.get("who_loses"))
        return {"outcome": SELECTED_VALID,
                "reason": "model selected the awarded mechanism with a named victim; checks 2-6 hold",
                "settling_check": "none (already selected)", "harness_required": False, "checks": checks}

    if disp == "unresolved":
        # Carried forward (not rejected) with an open question → recall-preserving. If a small static/differential
        # check would settle the open question, escalate to NEEDS_HARNESS; otherwise carry.
        feasible = bool(case.get("settling_check_feasible"))
        checks["carried_not_rejected"] = True
        checks["settling_check_feasible"] = feasible
        if feasible:
            return {"outcome": SELECTED_NEEDS_HARNESS,
                    "reason": "carried (not rejected); a minimal check would confirm the open precondition/bound",
                    "settling_check": case.get("settling_check", ""),
                    "harness_required": case.get("harness_required", True), "checks": checks}
        return {"outcome": UNRESOLVED_CARRY_FORWARD,
                "reason": "who-gains/who-loses or precondition genuinely open; carry forward, do not reject",
                "settling_check": case.get("settling_check", ""), "harness_required": False, "checks": checks}

    # disp == "rejected": the calibration-critical branch.
    resp = rejection_is_responsive(case.get("rejecting_fact", ""), case.get("alleged_locus_tokens", []),
                                   alleged_families, case.get("leans_on_unproven_guard", False))
    too_high = applies_too_high_severity_bar(case.get("rejecting_fact", ""), case["lowest_tier_cleared"])
    checks.update({"responsiveness": resp, "applies_too_high_severity_bar": too_high})

    if not resp["responsive"]:
        # Non-responsive: rebuts a different locus/family, or leans on an unproven guard.
        if not resp["locus_referenced"]:
            why = "non_responsive: rejecting fact does not reference the alleged bug locus"
        elif not resp["family_match"]:
            why = "non_responsive: rejecting fact addresses a different failure-mode family"
        else:
            why = "non_responsive: rejection leans on an unproven guard (should be carried)"
        return {"outcome": REJECTED_INCORRECTLY, "reason": why,
                "settling_check": case.get("settling_check", ""),
                "harness_required": case.get("harness_required", True), "checks": checks}

    if too_high:
        return {"outcome": REJECTED_INCORRECTLY,
                "reason": ("severity_floor: rejection rebuts only a higher tier; the mechanism clears "
                           f"{case['lowest_tier_cleared']} (e.g. DoS = Medium per the scale)"),
                "settling_check": case.get("settling_check", "static: confirm the mechanism clears its tier"),
                "harness_required": False, "checks": checks}

    # Responsive, proven, and at the right tier → a legitimate rejection.
    return {"outcome": REJECTED_VALIDLY,
            "reason": "rejection references the alleged locus + failure mode on a proven fact at the right tier",
            "settling_check": "none (validly rejected)", "harness_required": False, "checks": checks}


# ---------------------------------------------------------------------------------------------------------------
# Per-finding adjudication facts for the 9 P186 disagreement/stable cases.
# answer-aware INPUTS (legitimate in a calibration phase): `awarded_*`, `alleged_failure_mode`,
# `alleged_locus_tokens`, `lowest_tier_cleared`. FROZEN-MODEL INPUTS (parsed/transcribed from P186 raw_outputs):
# `model_disposition`, `rejecting_fact`, `who_loses`. Opus views are the frozen P184/P185 dispositions.
# ---------------------------------------------------------------------------------------------------------------
CASES = [
    {"finding": "H-07", "function": "onAfterRemoveLiquidity", "awarded_severity": "High",
     "alleged_failure_mode": "unauthorized deletion via attacker-controlled userData identity (access control)",
     "alleged_locus_tokens": ["userData", "bytes20", "userAddress"], "lowest_tier_cleared": "High",
     "source_evidence": "line 208: address userAddress = address(bytes20(userData));",
     "opus_view": "selected (P184/P185)", "model_disposition": "selected",
     "who_loses": "victim LP (positions deleted/burned)", "rejecting_fact": ""},

    {"finding": "M-02", "function": "onAfterRemoveLiquidity", "awarded_severity": "Medium",
     "alleged_failure_mode": "lpTokenDepositValueChange integer-division truncation/underflow in uplift fee calc",
     "alleged_locus_tokens": ["lpTokenDepositValueChange"], "lowest_tier_cleared": "Medium",
     "source_evidence": ("lines 241-243: lpTokenDepositValueChange = (int(now) - int(deposit)) / int(deposit) "
                         "— integer division truncates the ratio toward 0 (no 1e18 scaling)"),
     "opus_view": "carried/selected (P185)", "model_disposition": "rejected",
     "who_loses": "protocol (uplift fee bypassed / mis-set)", "leans_on_unproven_guard": False,
     "rejecting_fact": ("feePerLP 1e18 units, feeAmount 1e18 units, mulDown cancels scale; floors favour LP "
                        "(documented)"),
     "settling_check_feasible": True, "harness_required": True,
     "settling_check": ("differential / corrected-reference: recompute lpTokenDepositValueChange with 1e18 "
                        "scaling and compare to the on-chain integer-division result on one concrete "
                        "(now, deposit) input; assert fee != bypassed")},

    {"finding": "M-17", "function": "onAfterRemoveLiquidity", "awarded_severity": "Medium",
     "alleged_failure_mode": "feePerLP can exceed 100% (value exceeds a logical/economic bound)",
     "alleged_locus_tokens": ["feePerLP", "feePercentage"], "lowest_tier_cleared": "Medium",
     "source_evidence": "lines 247-281: feePerLP / feePercentage computed with no upper bound (<= 1e18) enforced",
     "opus_view": "carried (P185); not enumerated (P184)", "model_disposition": "unresolved",
     "who_loses": "withdrawing user (fee > 100%)",
     "settling_check_feasible": True, "harness_required": False,
     "settling_check": "static bound assertion: can feePerLP/feePercentage exceed 1e18 for in-range inputs?"},

    {"finding": "M-03", "function": "afterUpdate", "awarded_severity": "Medium",
     "alleged_failure_mode": "poolsFeeData[_to] length unchecked on transfer (push past the 100-deposit cap)",
     "alleged_locus_tokens": ["poolsFeeData", "length", "push"], "lowest_tier_cleared": "Medium",
     "source_evidence": "afterUpdate pushes to recipient FeeData array with no >100 check (addLiquidity has one)",
     "opus_view": "selected (P184)", "model_disposition": "unresolved",
     "who_loses": "recipient (array growth) / protocol invariant",
     "settling_check_feasible": True, "harness_required": True,
     "settling_check": "harness: transfer NFTs to push recipient array past 100; assert downstream iteration cost"},

    {"finding": "M-10", "function": "afterUpdate", "awarded_severity": "Medium",
     "alleged_failure_mode": "attacker permanently DoSes a victim from managing LP NFTs (malicious transfer)",
     "alleged_locus_tokens": ["poolsFeeData", "push", "transfer"], "lowest_tier_cleared": "Medium",
     "source_evidence": "same cap-bypass: attacker sends many NFTs, bloating victim array -> withdrawal bricks",
     "opus_view": "selected (P184, loose)", "model_disposition": "unresolved",
     "who_loses": "victim (cannot manage/withdraw LP NFTs)",
     "settling_check_feasible": True, "harness_required": True,
     "settling_check": "harness: grief victim array, assert their removeLiquidity reverts on gas/iteration"},

    {"finding": "L-01", "function": "afterUpdate", "awarded_severity": "Low",
     "alleged_failure_mode": "blockTimestampDeposit = block.number instead of block.timestamp / wrong type",
     "alleged_locus_tokens": ["blockTimestampDeposit", "block.number"], "lowest_tier_cleared": "Low",
     "source_evidence": "line 242: blockTimestampDeposit = uint32(block.number) vs deposit-path uint40(timestamp)",
     "opus_view": "selected (P184)", "model_disposition": "selected",
     "who_loses": "protocol (time-based fee corrupted)", "rejecting_fact": ""},

    {"finding": "H-03", "function": "onAfterSwap", "awarded_severity": "High",
     "alleged_failure_mode": "missing/improper fee application in swap logic (admin over-allocation)",
     "alleged_locus_tokens": ["adminFee", "quantAMMFeeTake", "hookFee"], "lowest_tier_cleared": "High",
     "source_evidence": "double integer truncation adminFee = hookFee/(1e18/quantAMMFeeTake) over-allocates admin",
     "opus_view": "selected (P184/P185, loose)", "model_disposition": "selected",
     "who_loses": "hook owner (receives less than configured)", "rejecting_fact": ""},

    {"finding": "M-06", "function": "UpdateWeightRunner._getData", "awarded_severity": "Medium",
     "alleged_failure_mode": "unhandled Chainlink revert locks all price-oracle access (external-call DoS)",
     "alleged_locus_tokens": ["latestRoundData", "_getOracleData", "revert", "No fresh oracle"],
     "lowest_tier_cleared": "Medium",
     "source_evidence": ("ChainlinkOracle._getData line 201: priceFeed.latestRoundData() with no try/catch; "
                         "UpdateWeightRunner line 157: revert('No fresh oracle values available') propagates"),
     "opus_view": "selected (P184)", "model_disposition": "rejected",
     "who_loses": "pool operators/LPs (no timely rebalance; oracle path locked)", "leans_on_unproven_guard": False,
     "rejecting_fact": ("revert propagates and reverts the weight-update; view function, no state mutation "
                        "before/after — liveness/DoS not fund-loss; no inconsistent state (view)"),
     "settling_check_feasible": True, "harness_required": False,
     "settling_check": ("static: a DoS that locks all oracle access clears Medium per the severity scale; the "
                        "'not fund-loss' rebuttal addresses only the High bar")},

    {"finding": "L-02", "function": "MultiHopOracle._getData", "awarded_severity": "Low",
     "alleged_failure_mode": "precision loss across hops (sequential floor-division truncation)",
     "alleged_locus_tokens": ["MultiHopOracle", "precision", "hops"], "lowest_tier_cleared": "Low",
     "source_evidence": "((A*B)/1e18*C)/1e18 sequential truncation across N hops grows with hop count",
     "opus_view": "selected (P184)", "model_disposition": "selected",
     "who_loses": "LPs (mispriced pool, arbitraged)", "rejecting_fact": ""},
]

# The 6 model-independent stable selections from P186 — anti-overfit control: NONE may be REJECTED_*.
STABLE_SELECTIONS = ["H-07", "M-03", "M-10", "L-01", "L-02", "H-03"]
# The two genuine P186 flips — the only cases the rubric should mark REJECTED_INCORRECTLY.
FLIPS = ["M-02", "M-06"]


def build_matrix() -> dict:
    rows = []
    for c in CASES:
        verdict = adjudicate(c)
        rows.append({
            "finding": c["finding"], "function": c["function"],
            "awarded": {"severity": c["awarded_severity"], "failure_mode": c["alleged_failure_mode"]},
            "opus_view": c["opus_view"], "sonnet_view": c["model_disposition"],
            "sonnet_rejecting_fact": c.get("rejecting_fact", "") or None,
            "source_evidence": c["source_evidence"],
            "outcome": verdict["outcome"], "reason": verdict["reason"],
            "settling_check": verdict["settling_check"], "harness_required": verdict["harness_required"],
            "checks": verdict["checks"],
            "is_stable_selection": c["finding"] in STABLE_SELECTIONS,
            "is_p186_flip": c["finding"] in FLIPS,
        })
    # Resolution-path classification for the decision section.
    resolution = {}
    for r in rows:
        if r["finding"] in FLIPS:
            resolution[r["finding"]] = ("severity_boundary_static" if "severity_floor" in r["reason"]
                                        else "execution_required" if r["harness_required"]
                                        else "static_rubric_resolvable")
    return {"phase": "P187", "research_only": True, "is_gate": False, "routes_in_production": False,
            "corpus": "quantamm-2024-12-eval", "no_recall_claim": True,
            "outcome_legend": [SELECTED_VALID, SELECTED_NEEDS_HARNESS, UNRESOLVED_CARRY_FORWARD,
                               REJECTED_VALIDLY, REJECTED_INCORRECTLY],
            "stable_selections": STABLE_SELECTIONS, "p186_flips": FLIPS,
            "flip_resolution_path": resolution, "rows": rows, **_FLAGS}


def main() -> int:
    # Read-only confirmation that the frozen Sonnet dispositions still match what the CASES table transcribes.
    drift = _verify_against_frozen_outputs()
    P187.mkdir(parents=True, exist_ok=True)
    matrix = build_matrix()
    matrix["frozen_output_consistency"] = drift
    (P187 / "adjudication_matrix.json").write_text(json.dumps(matrix, indent=2) + "\n")
    rej = [r["finding"] for r in matrix["rows"] if r["outcome"].startswith("REJECTED")]
    print(f"adjudication_matrix.json written: {len(matrix['rows'])} rows; "
          f"REJECTED_INCORRECTLY -> {[r['finding'] for r in matrix['rows'] if r['outcome']==REJECTED_INCORRECTLY]}; "
          f"any-rejected -> {rej}; frozen_consistency={drift['consistent']}")
    return 0


def _verify_against_frozen_outputs() -> dict:
    """Read-only: confirm each CASES disposition is consistent with the frozen P186 raw output (the mechanism
    appears in the matching bucket). Reports inconsistencies rather than mutating anything."""
    fmap = {"onAfterRemoveLiquidity": "onAfterRemoveLiquidity.json", "afterUpdate": "afterUpdate.json",
            "onAfterSwap": "onAfterSwap.json", "UpdateWeightRunner._getData": "UpdateWeightRunner__getData.json",
            "MultiHopOracle._getData": "MultiHopOracle__getData.json"}
    notes = []
    for c in CASES:
        fn = fmap.get(c["function"])
        p = P186 / "raw_outputs" / fn if fn else None
        if not p or not p.exists():
            notes.append(f"{c['finding']}: frozen output not found"); continue
        d = json.loads(p.read_text())
        buckets = {"selected": d.get("selected_mechanisms", []), "unresolved": d.get("unresolved_mechanisms", []),
                   "rejected": d.get("rejected_mechanisms", []) or d.get("rejection_table", [])}
        if not isinstance(buckets[c["model_disposition"]], list) or not buckets[c["model_disposition"]]:
            notes.append(f"{c['finding']}: disposition '{c['model_disposition']}' bucket empty in frozen output")
    return {"consistent": not notes, "notes": notes}


if __name__ == "__main__":
    raise SystemExit(main())
