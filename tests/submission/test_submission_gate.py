"""
Tests for the submission-readiness gate.

Mirrors the style of tests/poc_validation/test_poc_validation.py: the gate
modules live in submission/gates/, so we add that directory to sys.path and
import them via importlib. The gate is standalone (no audit_context, no
pipeline state), so tests just feed it candidate dicts / example files.

Run: /home/dummy/.local/bin/pytest tests/submission/ -v
"""
import copy
import importlib
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GATES = REPO / "submission" / "gates"
EXAMPLES = REPO / "submission" / "examples"
sys.path.insert(0, str(GATES))

_common = importlib.import_module("_common")
sg = importlib.import_module("submission_gate")
gate_scope = importlib.import_module("gate_scope")
gate_reachability = importlib.import_module("gate_reachability")
gate_impact_severity = importlib.import_module("gate_impact_severity")
gate_poc = importlib.import_module("gate_poc")
gate_duplicate = importlib.import_module("gate_duplicate")
gate_evidence = importlib.import_module("gate_evidence")
gate_defense = importlib.import_module("gate_defense")
gate_human_approval = importlib.import_module("gate_human_approval")


# --- helpers ----------------------------------------------------------------

def _load(name):
    return json.loads((EXAMPLES / name).read_text())


def _valid_base():
    """A fully-clean candidate that passes every gate (example 01)."""
    return copy.deepcopy(_load("01_valid_high_confidence.json"))


def _run_main(argv):
    old = sys.argv
    sys.argv = ["submission_gate"] + argv
    try:
        return sg.main()
    finally:
        sys.argv = old


def _verdicts(results):
    return [r.verdict for r in results]


# --- example files -> expected status ---------------------------------------

EXPECTED = {
    "01_valid_high_confidence.json": "READY_TO_SUBMIT_AFTER_APPROVAL",
    "02_needs_more_proof.json": "NEEDS_MORE_PROOF",
    "03_duplicate_risk.json": "READY_FOR_HUMAN_REVIEW",
    "04_out_of_scope.json": "DO_NOT_SUBMIT",
    "05_severity_inflated.json": "DO_NOT_SUBMIT",
    "06_privileged_only.json": "DO_NOT_SUBMIT",
}


@pytest.mark.parametrize("fname,expected", sorted(EXPECTED.items()))
def test_examples_resolve_to_expected_status(fname, expected):
    candidate = _load(fname)
    report = sg.evaluate_candidate(candidate)
    assert report["recommended_status"] == expected, report["gates"]


@pytest.mark.parametrize("fname", sorted(EXPECTED))
def test_examples_are_schema_valid(fname):
    errors = _common.validate_schema(_load(fname))
    assert errors == [], errors


@pytest.mark.parametrize("fname", sorted(EXPECTED))
def test_author_recommended_matches_computed(fname):
    # the example fixtures are authored to match what the gate computes
    candidate = _load(fname)
    report = sg.evaluate_candidate(candidate)
    assert report["recommended_status"] == candidate["recommended_status"]


# --- exit codes -------------------------------------------------------------

def test_exit_code_zero_for_ready(tmp_path):
    rc = _run_main(["--candidate", str(EXAMPLES / "01_valid_high_confidence.json"), "--quiet"])
    assert rc == 0


def test_exit_code_one_for_do_not_submit():
    rc = _run_main(["--candidate", str(EXAMPLES / "04_out_of_scope.json"), "--quiet"])
    assert rc == 1


def test_needs_more_proof_is_zero_without_strict():
    rc = _run_main(["--candidate", str(EXAMPLES / "02_needs_more_proof.json"), "--quiet"])
    assert rc == 0


def test_needs_more_proof_is_one_with_strict():
    rc = _run_main(["--candidate", str(EXAMPLES / "02_needs_more_proof.json"), "--quiet", "--strict"])
    assert rc == 1


def test_dir_run_blocks_when_any_do_not_submit(tmp_path):
    out = tmp_path / "verdicts.json"
    rc = _run_main(["--dir", str(EXAMPLES), "--quiet", "--json-out", str(out)])
    assert rc == 1  # at least one example is DO_NOT_SUBMIT
    payload = json.loads(out.read_text())
    assert payload["never_auto_submits"] is True
    assert len(payload["candidates"]) == len(EXPECTED)


def test_missing_input_returns_two():
    rc = _run_main(["--quiet"])
    assert rc == 2


# --- per-gate unit tests ----------------------------------------------------

def test_scope_blocks_admin_when_not_in_scope():
    c = _valid_base()
    c["privilege_required"] = "admin"
    c["bounty_program_mapping"]["privileged_roles_in_scope"] = False
    rs = gate_scope.evaluate(c)
    assert _common.FAIL in _verdicts(rs)
    assert any(r.tag == "privileged_only" for r in rs)


def test_scope_warns_admin_when_in_scope():
    c = _valid_base()
    c["privilege_required"] = "admin"
    c["bounty_program_mapping"]["privileged_roles_in_scope"] = True
    rs = gate_scope.evaluate(c)
    assert _common.FAIL not in _verdicts(rs)
    assert _common.WARN in _verdicts(rs)


def test_scope_blocks_excluded_vector():
    c = _valid_base()
    c["attacker_capabilities"] = ["phishing of end users"]
    rs = gate_scope.evaluate(c)
    assert any(r.tag == "excluded_vector" for r in rs)


def test_reachability_needs_proof_on_empty_call_trace():
    c = _valid_base()
    c["call_trace"] = []
    rs = gate_reachability.evaluate(c)
    assert _common.NEEDS_PROOF in _verdicts(rs)


def test_severity_inflation_fails_with_downgrade_note():
    c = _valid_base()
    c["impact_category"] = "dos"
    c["severity_claim"] = "Critical"
    rs = gate_impact_severity.evaluate(c)
    inflated = [r for r in rs if r.tag == "severity_inflated"]
    assert inflated, _verdicts(rs)
    assert inflated[0].verdict == _common.FAIL
    assert "supportable" in inflated[0].detail


def test_severity_within_ceiling_passes():
    c = _valid_base()  # High + fund_loss (ceiling Critical)
    rs = gate_impact_severity.evaluate(c)
    assert not any(r.tag == "severity_inflated" for r in rs)


def test_poc_forbidden_method_fails():
    c = _valid_base()
    c["invalidating_conditions"] = ["tested via a live mainnet attack"]
    rs = gate_poc.evaluate(c)
    assert any(r.tag == "forbidden_poc_method" and r.verdict == _common.FAIL for r in rs)


def test_poc_high_without_runnable_needs_proof():
    c = _valid_base()
    c["proof_type"] = "reasoning_only"
    c["poc_status"] = "none"
    c["poc_path"] = ""
    rs = gate_poc.evaluate(c)
    assert any(r.tag == "poc_required" and r.verdict == _common.NEEDS_PROOF for r in rs)


def test_duplicate_confirmed_fails():
    c = _valid_base()
    c["duplicate_check_status"] = "confirmed_duplicate"
    rs = gate_duplicate.evaluate(c)
    assert any(r.tag == "duplicate_finding" and r.verdict == _common.FAIL for r in rs)


def test_duplicate_not_searched_needs_proof():
    c = _valid_base()
    c["duplicate_check_status"] = "not_searched"
    c["known_issue_check_status"] = "not_searched"
    rs = gate_duplicate.evaluate(c)
    assert all(r.verdict == _common.NEEDS_PROOF for r in rs)


def test_evidence_needs_proof_on_empty_links():
    c = _valid_base()
    c["evidence_links"] = []
    rs = gate_evidence.evaluate(c)
    assert _common.NEEDS_PROOF in _verdicts(rs)


def test_defense_blocking_unrebutted_fails():
    c = _valid_base()
    c["defense_analysis"] = [{"defense": "nonReentrant", "blocks_path": True}]
    rs = gate_defense.evaluate(c)
    assert any(r.tag == "defense_blocks_path" and r.verdict == _common.FAIL for r in rs)


def test_defense_uncertain_warns():
    c = _valid_base()
    c["defense_analysis"] = [{"defense": "guard", "blocks_path": False,
                              "why_it_fails": "n/a", "uncertain": True}]
    rs = gate_defense.evaluate(c)
    assert _common.WARN in _verdicts(rs)


# --- invariants -------------------------------------------------------------

def test_human_approval_always_required_even_if_input_false():
    c = _valid_base()
    c["human_approval_required"] = False
    report = sg.evaluate_candidate(c)
    assert report["human_approval_required"] is True


def test_no_status_is_ever_submitted():
    for fname in EXPECTED:
        report = sg.evaluate_candidate(_load(fname))
        assert report["recommended_status"] in _common.STATUSES
        assert "submitted" not in report["recommended_status"].lower()


def test_fail_outranks_needs_proof_outranks_warn():
    # a candidate with a FAIL (scope) and a NEEDS_PROOF (evidence) resolves to FAIL
    c = _valid_base()
    c["scope_status"] = "out_of_scope"   # FAIL
    c["evidence_links"] = []              # NEEDS_PROOF
    c["duplicate_check_status"] = "possible_duplicate"  # WARN
    report = sg.evaluate_candidate(c)
    assert report["recommended_status"] == "DO_NOT_SUBMIT"


def test_needs_proof_outranks_warn():
    c = _valid_base()
    c["evidence_links"] = []                              # NEEDS_PROOF
    c["duplicate_check_status"] = "possible_duplicate"    # WARN
    report = sg.evaluate_candidate(c)
    assert report["recommended_status"] == "NEEDS_MORE_PROOF"


def test_schema_failure_blocks():
    c = _valid_base()
    del c["root_cause"]  # required field
    report = sg.evaluate_candidate(c)
    assert report["recommended_status"] == "DO_NOT_SUBMIT"
    assert report["schema_errors"]
