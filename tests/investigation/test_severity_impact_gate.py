"""Phase-81c tests for the promotion severity/impact gate (RESEARCH-ONLY) — closes the P81a D2 gap."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from investigation import severity_impact_gate as G  # noqa: E402


def test_1_self_test():
    assert G._self_test() == 0


def test_2_d2_dust_demoted():
    # the P81a D2 case: source-true but dust impact must NOT stay POC_REQUIRED
    r = G.gate("POC_REQUIRED", {"impact_class": "dust", "proven_magnitude": "transient", "source_true": True})
    assert r.kept is False and r.recommended_status == "NEEDS_CONTEXT"


def test_3_material_kept():
    for ic in ("critical", "high", "medium"):
        r = G.gate("POC_REQUIRED", {"impact_class": ic, "proven_magnitude": "material"})
        assert r.kept is True and r.recommended_status == "POC_REQUIRED"


def test_4_low_qa_informational_demoted():
    for ic in ("low", "qa", "informational", "gas"):
        r = G.gate("READY_FOR_HUMAN_REVIEW", {"impact_class": ic})
        assert r.kept is False and r.recommended_status == "NEEDS_CONTEXT"


def test_5_unproven_fail_closed():
    r = G.gate("POC_REQUIRED", {})
    assert r.kept is False and r.recommended_status == "NEEDS_CONTEXT"


def test_6_non_promotion_passthrough_never_repromotes():
    for d in ("NEEDS_CONTEXT", "REJECTED"):
        r = G.gate(d, {"impact_class": "high"})  # even with high impact, gate never RE-promotes a non-promotion
        assert r.kept is True and r.recommended_status == d


def test_7_gate_bundle_wrapper_and_flags():
    out = G.gate_bundle({"candidate_id": "X", "final_decision": "POC_REQUIRED",
                         "impact_assessment": {"impact_class": "dust"}})
    assert out["recommended_status"] == "NEEDS_CONTEXT" and out["candidate_id"] == "X"
    assert out["routes_in_production"] is False and out["research_only"] is True and out["is_gate"] is False


def test_8_never_promotes_above_input():
    # gate only ever keeps or demotes; it must never raise NEEDS_CONTEXT to POC_REQUIRED
    r = G.gate("NEEDS_CONTEXT", {"impact_class": "critical", "proven_magnitude": "material"})
    assert r.recommended_status == "NEEDS_CONTEXT"


# ---- P81f calibration regression (control c + case d) ----

def test_9_p81f_dust_revert_control_still_demotes():
    # (c) the P81a D2 dust/revert-only control must STILL demote after calibration
    d2 = G.gate("POC_REQUIRED", {"impact_class": "dust", "proven_magnitude": "transient", "material_consequence": []})
    assert d2.kept is False and d2.recommended_status == "NEEDS_CONTEXT"
    # a 'low' candidate whose only basis is conservative wording (no material consequence) still demotes
    revert_only = G.gate("POC_REQUIRED", {"impact_class": "low", "material_consequence": []})
    assert revert_only.kept is False


def test_10_p81f_true_medium_material_not_auto_demoted():
    # (d) a low-labelled candidate with a SOURCE-BACKED material consequence (M-04 / M-01 style) is NOT auto-demoted
    for tags in (["denial_of_asset_movement", "failed_settlement"], ["stuck_funds"], ["loss_of_capital"], ["unauthorized_execution"]):
        r = G.gate("POC_REQUIRED", {"impact_class": "low", "source_true": True, "material_consequence": tags})
        assert r.kept is True and r.recommended_status == "POC_REQUIRED", tags
    # gating: material consequence only counts when source_true
    assert G.gate("POC_REQUIRED", {"impact_class": "low", "source_true": False, "material_consequence": ["fund_loss"]}).kept is False
    # and a dust CLASS still demotes even if a material tag is mis-attached (D2 robustness)
    assert G.gate("POC_REQUIRED", {"impact_class": "dust", "material_consequence": ["fund_loss"]}).kept is False


# ---- P86 cross-eval severity-calibration regression anchors ----

def test_p86_a1_updatetaxrate_bounded_accounting_demoted():
    # ANCHOR 1: the P85 severity FP — updateTaxRate, a bounded/lazy-settlement accounting issue tagged
    # misrouted_funds and (over-)labelled Medium with material magnitude, MUST now demote.
    r = G.gate("POC_REQUIRED", {"impact_class": "medium", "proven_magnitude": "material",
                                "source_true": True, "material_consequence": ["misrouted_funds"]})
    assert r.kept is False and r.recommended_status == "NEEDS_CONTEXT"
    # also with explicit bounded markers
    r2 = G.gate("POC_REQUIRED", {"impact_class": "medium",
                                 "bounded_markers": ["bounded_rate_mismatch", "no_quantified_user_loss",
                                                     "no_blocked_claim_withdraw_settlement_path"],
                                 "material_consequence": []})
    assert r2.kept is False


def test_p86_declared_high_with_only_bounded_consequence_demotes():
    # the "declared High saves weak evidence" regression: high/critical class but the ONLY consequence is
    # bounded/non-material (misrouted_funds / stale_parameter, no concrete) -> demote.
    for ic in ("high", "critical"):
        for tag in ("misrouted_funds", "stale_parameter", "accounting_drift"):
            r = G.gate("POC_REQUIRED", {"impact_class": ic, "proven_magnitude": "material",
                                        "source_true": True, "material_consequence": [tag]})
            assert r.kept is False, f"{ic} + {tag} should demote (bounded-only, not concrete)"


def test_p86_a2_h05_reward_loss_kept():
    # ANCHOR 2: H-05 dirty-flag-never-reset — permanent reward loss is source-backed -> KEEP.
    for tags in (["reward_loss_not_recoverable"], ["stuck_funds", "user_loss"]):
        r = G.gate("POC_REQUIRED", {"impact_class": "high", "source_true": True, "material_consequence": tags})
        assert r.kept is True and r.recommended_status == "POC_REQUIRED", tags


def test_p86_a3_p81e_h03_liveness_kept():
    # ANCHOR 3: P81e H-03-style DoS/liveness/launch-failure with a source-backed material consequence -> KEEP.
    for tags in (["denial_of_asset_movement"], ["failed_settlement"]):
        r = G.gate("POC_REQUIRED", {"impact_class": "high", "proven_magnitude": "material",
                                    "source_true": True, "material_consequence": tags})
        assert r.kept is True, tags


def test_p86_a4_p81d_m04_m01_failed_settlement_kept():
    # ANCHOR 4: P81d M-04/M-01 true Mediums (failed settlement / denial of asset movement) -> KEEP.
    for ic in ("low", "medium"):
        for tags in (["failed_settlement"], ["denial_of_asset_movement"]):
            r = G.gate("POC_REQUIRED", {"impact_class": ic, "source_true": True, "material_consequence": tags})
            assert r.kept is True, (ic, tags)


def test_p86_a5_d2_dust_still_demoted():
    # ANCHOR 5: P81a D2 swapNoPath dust/revert remains demoted.
    r = G.gate("POC_REQUIRED", {"impact_class": "dust", "proven_magnitude": "transient", "source_true": True})
    assert r.kept is False and r.recommended_status == "NEEDS_CONTEXT"


def test_p86_a6_controls_rejected_passthrough():
    # ANCHOR 6: guarded admin/onlyOwner controls are REJECTED upstream (deep_pass); the gate must pass a
    # REJECTED decision through unchanged and never re-promote it, even with a high impact_class.
    r = G.gate("REJECTED", {"impact_class": "high", "material_consequence": ["unauthorized_execution"]})
    assert r.kept is True and r.recommended_status == "REJECTED"


def test_p86_bounded_plus_concrete_keeps_via_concrete():
    # a candidate carrying BOTH a bounded tag and a concrete tag -> concrete wins -> KEEP.
    r = G.gate("POC_REQUIRED", {"impact_class": "medium", "source_true": True,
                                "material_consequence": ["misrouted_funds", "stuck_funds"]})
    assert r.kept is True


def test_p86_misrouted_funds_alone_no_longer_lifts_low():
    # misrouted_funds is intentionally NOT concrete -> a low backed only by it demotes.
    r = G.gate("POC_REQUIRED", {"impact_class": "low", "source_true": True, "material_consequence": ["misrouted_funds"]})
    assert r.kept is False


# ---- P88 under-rating / liveness calibration regression anchors (A-G) ----

def test_p88_a_h01_liveness_not_underrated_and_high_rationale():
    # ANCHOR A: P87 H-01 mintWithBudget (global counter vs per-gen limit -> permanent mint brick).
    # Kept, never under-rated below Medium; with high_liveness markers the gate reports `high`.
    r = G.gate("POC_REQUIRED", {"impact_class": "medium", "source_true": True,
                                "material_consequence": ["permanent_function_brick", "blocked_mint_path"],
                                "liveness_markers": ["bricks_major_phase_or_generation", "many_or_all_users_affected"]})
    assert r.kept is True and r.impact_class == "high"
    # even if an analyst under-labels it 'low', a source-backed liveness consequence keeps it >= medium
    low = G.gate("POC_REQUIRED", {"impact_class": "low", "source_true": True, "material_consequence": ["blocked_mint_path"]})
    assert low.kept is True and low.impact_class in ("medium", "high")


def test_p88_b_m18_involuntary_race_kept():
    # ANCHOR B: P87 M-18 forgeWithListed involuntary fee-reduction race -> stuck funds. Keep as Medium.
    r = G.gate("POC_REQUIRED", {"impact_class": "medium", "source_true": True,
                                "material_consequence": ["stuck_funds"], "involuntary": ["race_condition"]})
    assert r.kept is True
    # involuntary protection holds even when a bounded marker is (mistakenly) attached alongside the concrete loss
    mixed = G.gate("POC_REQUIRED", {"impact_class": "medium", "source_true": True,
                                    "material_consequence": ["stuck_funds"], "involuntary": ["race_condition"],
                                    "bounded_markers": ["no_blocked_claim_withdraw_settlement_path"]})
    assert mixed.kept is True


def test_p88_b_self_inflicted_no_loss_still_demoted():
    # the OTHER side of B: a voluntary/avoidable issue with no concrete loss still demotes (no over-keep).
    r = G.gate("POC_REQUIRED", {"impact_class": "low", "source_true": True, "material_consequence": [],
                                "bounded_markers": ["avoidable_by_normal_action_no_race", "no_quantified_user_loss"]})
    assert r.kept is False


def test_p88_c_updatetaxrate_still_demoted_even_with_involuntary_marker():
    # ANCHOR C (preserve P86): bounded/lazy with only misrouted_funds/stale_parameter + NO concrete still demotes,
    # even if declared High and even if an involuntary marker is attached (no free pass).
    assert G.gate("POC_REQUIRED", {"impact_class": "medium", "proven_magnitude": "material", "source_true": True,
                                   "material_consequence": ["misrouted_funds"]}).kept is False
    assert G.gate("POC_REQUIRED", {"impact_class": "high", "source_true": True,
                                   "material_consequence": ["stale_parameter"], "involuntary": ["race_condition"]}).kept is False


def test_p88_d_h05_reward_lifecycle_kept():
    # ANCHOR D: P85 H-05 dirty flag -> material reward loss kept.
    r = G.gate("POC_REQUIRED", {"impact_class": "high", "source_true": True, "material_consequence": ["reward_loss_not_recoverable"]})
    assert r.kept is True


def test_p88_e_p81e_liveness_kept():
    # ANCHOR E: P81e H-03 liveness / failed launch with denial_of_asset_movement or failed_settlement kept.
    for tag in ("denial_of_asset_movement", "failed_settlement"):
        assert G.gate("POC_REQUIRED", {"impact_class": "high", "source_true": True, "material_consequence": [tag]}).kept is True


def test_p88_f_d2_dust_still_demoted():
    # ANCHOR F: D2 dust still demotes (class floor + magnitude), even with a liveness tag mis-attached.
    assert G.gate("POC_REQUIRED", {"impact_class": "dust", "proven_magnitude": "transient", "source_true": True}).kept is False
    assert G.gate("POC_REQUIRED", {"impact_class": "dust", "source_true": True, "material_consequence": ["blocked_mint_path"]}).kept is False


def test_p88_g_controls_rejected_passthrough():
    # ANCHOR G: guarded controls -> REJECTED passthrough, never re-promoted (even with liveness/involuntary tags).
    r = G.gate("REJECTED", {"impact_class": "high", "material_consequence": ["denial_of_asset_movement"], "involuntary": ["race_condition"]})
    assert r.kept is True and r.recommended_status == "REJECTED"


def test_p88_declared_high_bounded_only_still_demotes():
    # explicit: declared High with ONLY bounded/non-material tags still demotes (no liveness/involuntary/concrete).
    for tag in ("misrouted_funds", "stale_parameter", "accounting_drift", "estimation_mismatch"):
        assert G.gate("POC_REQUIRED", {"impact_class": "high", "source_true": True, "material_consequence": [tag]}).kept is False
