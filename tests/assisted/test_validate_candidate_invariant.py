"""P98 tests for the assisted-mode candidate validator (RESEARCH-ONLY, un-wired).

Proves the reject-first decision precedence: no invariant -> blocked; a wrong-invariant input is rejected
WITHOUT becoming a finding; a PASS_CANDIDATE reaches VALIDATED_FOR_POC_HANDOFF only after hygiene + severity +
ordering pass; a severity FP blocks handoff; the bundle is generated; nothing auto-submits.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
sys.path.insert(0, str(ROOT / "scripts" / "investigation"))
import validate_candidate_invariant as V  # noqa: E402


INV = "a user cannot list/sell more than maxSellPercent of their original allocation"


def _good_trace(**over):
    t = {
        "localized_mechanism": "VestingManager.listVesting sellLimit vs maxSellPercent",
        "controlled_inputs": "EOA seller + sybil buyer; repeated cycles",
        "pre_state": "allocations[seller].sold/bought; original alloc A; maxSellPercent=2000",
        "operation_trace": "buy grows bought -> raises sellLimit; cycle re-lists",
        "boundary_cases": "cumulative cartel sold > maxSellPercent*A; per-user require never trips",
        "post_state": "restriction defeated",
        "concrete_outcome": "PASS",
    }
    t.update(over)
    return t


def _good_ord(**over):
    o = {
        "relied_upon_invariant": INV, "mechanism_class": "accounting",
        "counterexample_found": True,
        "counterexample_trace": "buy/resell cycles inflate bought, raising sellLimit beyond the cap",
    }
    o.update(over)
    return o


def _good_impact(**over):
    ia = {"impact_class": "medium", "proven_magnitude": "significant", "source_true": True,
          "source_backed": True, "material_consequence": ["denial_of_asset_movement"]}
    ia.update(over)
    return ia


def test_self_test_passes():
    assert V._self_test() == 0


def test_missing_invariant_blocked():
    r = V.validate({"contract": "C", "function": "f"})
    assert r.decision == V.BLOCKED_UNSUPPORTED


def test_empty_invariant_blocked():
    r = V.validate({"candidate_invariant": "   ", "depth_trace": _good_trace()})
    assert r.decision == V.BLOCKED_UNSUPPORTED


def test_no_trace_needs_context():
    assert V.validate({"candidate_invariant": INV}).decision == V.NEEDS_CONTEXT


def test_wrong_invariant_rejected_without_becoming_finding():
    """The P97 class: a true-but-irrelevant invariant + orderings that preserve it -> proven safe, NOT a finding."""
    reject_trace = _good_trace(concrete_outcome="REJECT",
                               boundary_cases="cap holds: moving tokens to sybil consumes seller cap",
                               post_state="conserves; no cap multiplication")
    reject_ord = {"relied_upon_invariant": "token sum is conserved", "mechanism_class": "accounting",
                  "ordering_cases_tested": ["list-then-buy", "claim-then-list", "sybil wash"],
                  "counterexample_found": False}
    r = V.validate({"candidate_invariant": "token sum conserved", "depth_trace": reject_trace,
                    "adversarial_ordering": reject_ord})
    assert r.decision == V.REJECTED_SAFE
    # crucially NOT a validated/handoff state
    assert r.decision != V.VALIDATED


def test_pass_candidate_validated_only_after_all_checks():
    r = V.validate({"candidate_invariant": INV, "depth_trace": _good_trace(),
                    "adversarial_ordering": _good_ord(), "impact_assessment": _good_impact()})
    assert r.decision == V.VALIDATED
    # all five check results are populated on the validated path
    assert r.trace_result and r.ordering_result and r.consequence_result and r.severity_result and r.hygiene_result


def test_severity_fp_blocks_handoff():
    fp = {"impact_class": "dust", "proven_magnitude": "transient", "source_true": True}
    r = V.validate({"candidate_invariant": INV, "depth_trace": _good_trace(),
                    "adversarial_ordering": _good_ord(), "impact_assessment": fp})
    assert r.decision == V.BLOCKED_UNSUPPORTED


def test_pass_candidate_without_impact_needs_context():
    r = V.validate({"candidate_invariant": INV, "depth_trace": _good_trace(),
                    "adversarial_ordering": _good_ord()})
    assert r.decision == V.NEEDS_CONTEXT


def test_ordering_reopen_needs_context():
    reopen = {"relied_upon_invariant": INV, "mechanism_class": "accounting",
              "ordering_cases_tested": ["only one"], "counterexample_found": False}
    r = V.validate({"candidate_invariant": INV, "depth_trace": _good_trace(),
                    "adversarial_ordering": reopen, "impact_assessment": _good_impact()})
    assert r.decision == V.NEEDS_CONTEXT


def test_submission_package_blocks_on_pending_scope_dup():
    r = V.validate({"candidate_invariant": INV, "depth_trace": _good_trace(),
                    "adversarial_ordering": _good_ord(), "impact_assessment": _good_impact(),
                    "requested_check": "SUBMISSION_PACKAGE"})
    assert r.decision == V.BLOCKED_SCOPE_DUP


def test_submission_package_allowed_when_human_cleared():
    r = V.validate({"candidate_invariant": INV, "depth_trace": _good_trace(),
                    "adversarial_ordering": _good_ord(), "impact_assessment": _good_impact(),
                    "requested_check": "SUBMISSION_PACKAGE",
                    "scope_check_status": "IN_SCOPE", "duplicate_check_status": "CLEAR"})
    assert r.decision == V.VALIDATED


def test_bundle_written(tmp_path):
    intake = {"subject": "secondswap-2024-12", "contract": "VM", "function": "listVesting",
              "candidate_invariant": INV, "supplied_by": "human", "requested_check": "VALIDATE",
              "depth_trace": _good_trace(), "adversarial_ordering": _good_ord(),
              "impact_assessment": _good_impact()}
    res = V.validate(intake)
    written = V.write_bundle(intake, res, tmp_path)
    for name in ("validation_report.md", "trace.json", "ordering_check.json",
                 "consequence_check.json", "severity_gate.json", "decision.json"):
        assert (tmp_path / name).exists(), name
    dec = json.loads((tmp_path / "decision.json").read_text())
    assert dec["decision"] == V.VALIDATED
    # decision.json never carries a SUBMITTED marker / production routing
    assert dec["routes_in_production"] is False and dec["is_gate"] is False


def test_example_candidate_validates():
    ex = ROOT / "documentation/research/assisted_mode/example_candidate.json"
    intake = json.loads(ex.read_text())
    assert V.validate(intake).decision == V.VALIDATED


def test_flags_unwired():
    assert V.FLAGS["is_gate"] is False
    assert V.FLAGS["research_only"] is True
    assert V.FLAGS["routes_in_production"] is False
