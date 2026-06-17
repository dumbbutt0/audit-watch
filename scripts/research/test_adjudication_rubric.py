#!/usr/bin/env python3
"""Tests for the P187 research-only adjudication rubric. Validate the two checks that close the P186 gap
(#8 non-responsive rejection, #7 severity floor) and the anti-overfit control (no stable selection is rejected)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adjudication_rubric as ar  # noqa: E402


# ---- #8 responsiveness ----------------------------------------------------------------------------------------
def test_units_rebuttal_of_underflow_is_non_responsive():
    """M-02 shape: a units-consistency rejecting fact that never names the alleged underflow locus is non-responsive."""
    r = ar.rejection_is_responsive(
        "feePerLP 1e18 units, feeAmount 1e18 units, mulDown cancels scale; floors favour LP",
        alleged_locus_tokens=["lpTokenDepositValueChange"],
        alleged_families=ar.families_of("lpTokenDepositValueChange integer-division truncation/underflow"),
        leans_on_unproven_guard=False)
    assert r["locus_referenced"] is False
    assert r["responsive"] is False


def test_responsive_when_locus_and_family_match_on_proven_fact():
    r = ar.rejection_is_responsive(
        "lpTokenDepositValueChange is scaled by 1e18 before division, so no truncation occurs",
        alleged_locus_tokens=["lpTokenDepositValueChange"],
        alleged_families=ar.families_of("lpTokenDepositValueChange integer-division truncation"),
        leans_on_unproven_guard=False)
    assert r["locus_referenced"] is True and r["responsive"] is True


def test_unproven_guard_breaks_responsiveness():
    r = ar.rejection_is_responsive(
        "lpTokenDepositValueChange truncation is caught by a downstream bound (assumed)",
        alleged_locus_tokens=["lpTokenDepositValueChange"],
        alleged_families=ar.families_of("lpTokenDepositValueChange truncation"),
        leans_on_unproven_guard=True)
    assert r["responsive"] is False


# ---- #7 severity floor ----------------------------------------------------------------------------------------
def test_dos_rejected_on_fundloss_bar_is_too_high():
    """M-06 shape: rejecting a Medium-clearing DoS for not being fund-loss applies a too-high bar."""
    assert ar.applies_too_high_severity_bar(
        "liveness/DoS not fund-loss; view function", lowest_tier_cleared="Medium") is True


def test_high_finding_rejected_on_fundloss_bar_is_not_too_high():
    """If the mechanism needs to clear High anyway, a fund-loss rebuttal is on-point, not a floor error."""
    assert ar.applies_too_high_severity_bar(
        "not fund-loss", lowest_tier_cleared="High") is False


# ---- decision tree --------------------------------------------------------------------------------------------
def test_m02_outcome_rejected_incorrectly_non_responsive():
    c = next(c for c in ar.CASES if c["finding"] == "M-02")
    v = ar.adjudicate(c)
    assert v["outcome"] == ar.REJECTED_INCORRECTLY
    assert "non_responsive" in v["reason"]
    assert v["harness_required"] is True            # settled by a differential check (execution)


def test_m06_outcome_rejected_incorrectly_severity_floor():
    c = next(c for c in ar.CASES if c["finding"] == "M-06")
    v = ar.adjudicate(c)
    assert v["outcome"] == ar.REJECTED_INCORRECTLY
    assert "severity_floor" in v["reason"]
    assert v["harness_required"] is False           # settled statically by the tier rule


def test_anti_overfit_no_stable_selection_is_rejected():
    """The 6 model-independent stable selections must NEVER land in a REJECTED_* bucket — and the rubric must
    not need any per-finding patch to achieve that."""
    for c in ar.CASES:
        if c["finding"] in ar.STABLE_SELECTIONS:
            assert not ar.adjudicate(c)["outcome"].startswith("REJECTED"), c["finding"]


def test_only_the_two_flips_are_rejected_incorrectly():
    rejected = [c["finding"] for c in ar.CASES
                if ar.adjudicate(c)["outcome"] == ar.REJECTED_INCORRECTLY]
    assert sorted(rejected) == sorted(ar.FLIPS)


def test_research_flags_present_and_ungated():
    assert ar._FLAGS["research_only"] is True
    assert ar._FLAGS["is_gate"] is False
    assert ar._FLAGS["routes_in_production"] is False


def test_matrix_builds_and_is_well_formed():
    m = ar.build_matrix()
    assert len(m["rows"]) == 9
    assert m["is_gate"] is False and m["research_only"] is True
    assert set(m["flip_resolution_path"]) == set(ar.FLIPS)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
