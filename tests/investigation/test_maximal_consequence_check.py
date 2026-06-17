"""P90 tests for the advisory maximal-consequence impact check (RESEARCH-ONLY, un-wired).

Covers the under-rating regression targets (P89 H-05, P87 H-01), admin-footgun (P87 H-03), involuntary
(P87 M-18), reject-first (no source -> no escalation), P86 preservation (bounded -> no escalation), and an
END-TO-END check that the recommended markers drive the UNCHANGED severity gate to `high`.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "investigation"))
from investigation import maximal_consequence_check as M  # noqa: E402
from investigation import severity_impact_gate as G  # noqa: E402


def test_self_test_passes():
    assert M._self_test() == 0


def test_h05_escalates_high_with_markers():
    a = M.assess({"base_impact_class": "medium", "source_backed": True,
                  "many_or_all_users_affected": True, "mass_dos_or_permanent_state_corruption": True,
                  "material_consequence": ["unauthorized_execution"]})
    assert a.escalate and a.recommended_impact_class == "high" and a.attach_high_markers


def test_h01_core_brick_escalates_high():
    a = M.assess({"base_impact_class": "medium", "source_backed": True,
                  "core_protocol_lifecycle_function": True, "permanent_unrecoverable_without_privileged": True,
                  "many_or_all_users_affected": True})
    assert a.escalate and a.recommended_impact_class == "high"


def test_reject_first_no_source_no_escalation():
    a = M.assess({"base_impact_class": "medium", "source_backed": False, "many_or_all_users_affected": True})
    assert not a.escalate and a.recommended_impact_class == "medium" and not a.attach_high_markers


def test_involuntary_concrete_kept_not_self_inflicted():
    a = M.assess({"base_impact_class": "medium", "source_backed": True, "involuntary": True,
                  "material_consequence": ["stuck_funds"]})
    assert not a.escalate and a.attach_involuntary


def test_admin_footgun_distinction():
    fg = M.assess({"base_impact_class": "low", "admin_initiated": True})
    assert fg.footgun_flag and not fg.escalate
    user = M.assess({"base_impact_class": "medium", "source_backed": True, "admin_initiated": True,
                     "externally_triggerable_user_harm": True})
    assert not user.footgun_flag


def test_p86_preserved_bounded_not_escalated():
    # bounded misrouted_funds with no high escalator -> the check does NOT escalate (gate still demotes it)
    a = M.assess({"base_impact_class": "medium", "source_backed": True, "material_consequence": ["misrouted_funds"]})
    assert not a.escalate


def test_end_to_end_markers_drive_unchanged_gate_to_high():
    # the check's recommended markers, attached to the impact_assessment, make the EXISTING P88 gate report high.
    a = M.assess({"base_impact_class": "medium", "source_backed": True,
                  "many_or_all_users_affected": True, "core_protocol_lifecycle_function": True,
                  "material_consequence": ["permanent_function_brick"]})
    ia = {"impact_class": a.recommended_impact_class, "source_true": True,
          "material_consequence": ["permanent_function_brick"], "liveness_markers": a.attach_high_markers}
    g = G.gate("POC_REQUIRED", ia)
    assert g.kept and g.impact_class == "high"


def test_advisory_never_demotes_or_routes():
    # the check only recommends; it carries research-only flags and never emits a routing/keep/demote verdict.
    assert M.FLAGS["routes_in_production"] is False and M.FLAGS["is_gate"] is False
    # a plain medium with nothing asserted -> base unchanged, no escalation, no footgun
    a = M.assess({"base_impact_class": "medium"})
    assert not a.escalate and not a.footgun_flag and a.recommended_impact_class == "medium"
