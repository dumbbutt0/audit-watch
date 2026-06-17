"""
Tests for the PoC validation layer (collector + validator + gate) — deterministic, no LLM/network/forge.

Core principle under test: a passing test is not proof. The validator only upgrades to `proven` when the
reviewer attests root-cause + reachability + state-transition + impact AND the structural checks hold; it
downgrades on storage-mutation/prank-as-admin/revert-only/overclaim. The gate never blocks eval, and blocks
unproven/overclaimed High/Critical in submission mode. Mirrors tests/confirm style.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
collect = importlib.import_module("collect_poc_results")
validate = importlib.import_module("validate_poc")
gate = importlib.import_module("poc_validation_gate")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output" / "poc_validation").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _write(ws, rel, obj):
    p = ws / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) if not isinstance(obj, str) else obj)
    return p


def _cand(fid, sev="High", refs=("function:A:f#x",), fns=("A.f",), title=None, ptype="unit"):
    return {"finding_id": fid, "title": title or f"{fid} loss of funds", "severity_ceiling": sev,
            "source": "merged_findings", "manifest_refs": list(refs), "affected_functions": list(fns),
            "affected_files": ["src/A.sol"], "poc_required": True, "required_proof_type": ptype,
            "minimum_proof_goal": "prove it", "suggested_test_strategy": "unit",
            "required_attacker_entrypoint": "A.f", "required_impact_assertion": "balance drop",
            "duplicate_candidates": [], "status": "missing_poc"}


def _inv(ws, cands):
    _write(ws, "output/poc_validation/poc_inventory.json",
           {"total": len(cands), "poc_required": len(cands), "candidates": cands})


def _note(fid, **over):
    base = {"poc_id": f"POCV-{fid}", "finding_id": fid, "test_type": "unit",
            "validation_status": "proven", "root_cause_proven": True,
            "attacker_reachability_proven": True, "impact_proven": True,
            "state_transition_proven": True, "severity_supported": "High",
            "why_test_proves_claim": "calls A.f as EOA; balance before 100 after 0",
            "limitations": "single fork block", "test_file": "test/A.t.sol",
            "test_name": "test_drain", "command_exit_code": 0}
    base.update(over)
    return base


GOOD_TEST = ("import 'forge-std/Test.sol';\ncontract T is Test {\n"
             "  function test_drain() public {\n"
             "    uint256 pre = token.balanceOf(victim);\n"
             "    vm.prank(attacker); target.f();\n"
             "    assertEq(token.balanceOf(victim), 0);\n  }\n}\n")
STORE_TEST = ("contract T is Test {\n  function test_drain() public {\n"
              "    vm.store(address(target), bytes32(uint256(3)), bytes32(uint256(1)));\n"
              "    assertEq(target.flag(), 1);\n  }\n}\n")
REVERT_ONLY_TEST = ("contract T is Test {\n  function test_drain() public {\n"
                    "    vm.expectRevert();\n    target.f();\n  }\n}\n")


def _run(mod, argv):
    old = sys.argv
    sys.argv = [mod.__name__] + argv
    try:
        return mod.main()
    finally:
        sys.argv = old


def _results(ws):
    return {r["finding_id"]: r for r in
            json.loads((ws / "output/poc_validation/poc_validation_results.json").read_text())["results"]}


# ---------------------------------------------------------------- tests

def test_valid_proven_unit_poc_passes(ws):
    _inv(ws, [_cand("F1")])
    _write(ws, "test/A.t.sol", GOOD_TEST + "\n// negative_control: unauthorized actor reverts\n")
    _write(ws, "output/poc_validation/validation_notes/F1.json", _note("F1"))
    _write(ws, "output/poc_validation/collected_results.json",
           {"results": [{"finding_id": "F1", "test_name": "test_drain", "test_file": "test/A.t.sol",
                         "command_exit_code": 0, "test_status": "passed"}]})
    assert _run(validate, []) == 0
    r = _results(ws)["F1"]
    assert r["validation_status"] == "proven"
    assert r["submission_ready"] is True


def test_passing_test_without_impact_assertion_is_partial(ws):
    _inv(ws, [_cand("F2")])
    _write(ws, "test/A.t.sol", GOOD_TEST)
    _write(ws, "output/poc_validation/validation_notes/F2.json",
           _note("F2", validation_status="partially_proven", impact_proven=False, severity_supported="Medium"))
    _run(validate, [])
    r = _results(ws)["F2"]
    assert r["validation_status"] in ("partially_proven", "inconclusive")
    assert r["submission_ready"] is False
    assert "impact_not_proven" in r["failed_requirements"]


def test_direct_storage_mutation_is_setup_only(ws):
    _inv(ws, [_cand("F3")])
    _write(ws, "test/A.t.sol", STORE_TEST)
    # reviewer over-claims proven, but storage write is not disclosed as setup -> downgraded
    _write(ws, "output/poc_validation/validation_notes/F3.json", _note("F3", test_name="test_drain"))
    _run(validate, [])
    r = _results(ws)["F3"]
    assert r["validation_status"] in ("setup_only", "invalid_poc")
    assert r["submission_ready"] is False


def test_high_without_poc_fails_submission(ws):
    _inv(ws, [_cand("F4", sev="High")])
    _run(validate, [])
    assert _results(ws)["F4"]["validation_status"] == "inconclusive"
    assert _run(gate, ["--mode", "submission"]) == 1
    rep = json.loads((ws / "output/poc_validation/poc_validation_gate.json").read_text())
    assert any(b["finding_id"] == "F4" for b in rep["blocking"])


def test_eval_mode_passes_without_poc(ws):
    _inv(ws, [_cand("F5", sev="High")])
    _run(validate, [])
    assert _run(gate, ["--mode", "eval"]) == 0
    rep = json.loads((ws / "output/poc_validation/poc_validation_gate.json").read_text())
    assert rep["passed"] is True and rep["blocking"] == []


def test_medium_partial_passes_engagement_with_warning(ws):
    _inv(ws, [_cand("F6", sev="Medium")])
    _write(ws, "test/A.t.sol", GOOD_TEST)
    _write(ws, "output/poc_validation/validation_notes/F6.json",
           _note("F6", validation_status="partially_proven", impact_proven=False, severity_supported="Medium"))
    _run(validate, [])
    r = _results(ws)["F6"]
    assert r["validation_status"] == "partially_proven"
    assert r["warnings"]  # carries warnings (e.g. no negative control / no value assertion)
    assert _run(gate, ["--mode", "engagement"]) == 0


def test_missing_negative_control_warns(ws):
    _inv(ws, [_cand("F7")])
    _write(ws, "test/A.t.sol", GOOD_TEST)  # no "negative_control" marker
    _write(ws, "output/poc_validation/validation_notes/F7.json", _note("F7"))
    _write(ws, "output/poc_validation/collected_results.json",
           {"results": [{"finding_id": "F7", "test_name": "test_drain", "test_file": "test/A.t.sol",
                         "command_exit_code": 0}]})
    _run(validate, [])
    assert "no_negative_control_detected" in _results(ws)["F7"]["warnings"]


def test_severity_overclaim_blocks_submission(ws):
    _inv(ws, [_cand("F8", sev="High")])
    _write(ws, "test/A.t.sol", GOOD_TEST)
    _write(ws, "output/poc_validation/validation_notes/F8.json",
           _note("F8", severity_supported="Low"))  # demonstrated impact only Low
    _write(ws, "output/poc_validation/collected_results.json",
           {"results": [{"finding_id": "F8", "test_name": "test_drain", "test_file": "test/A.t.sol",
                         "command_exit_code": 0}]})
    _run(validate, [])
    r = _results(ws)["F8"]
    assert r["severity_overclaim"] is True
    assert r["submission_ready"] is False
    assert _run(gate, ["--mode", "submission"]) == 1


def test_duplicate_proof_recognized(ws):
    _inv(ws, [_cand("F9")])
    _write(ws, "test/A.t.sol", GOOD_TEST)
    _write(ws, "output/poc_validation/validation_notes/F9.json",
           _note("F9", validation_status="duplicate_proof"))
    _run(validate, [])
    assert _results(ws)["F9"]["validation_status"] == "duplicate_proof"


def test_command_failure_records_failed(ws):
    # collector records a non-zero command without deciding proof
    rc = _run(collect, ["--finding-id", "F10", "--test-name", "test_x",
                        "--command", "sh -c 'echo boom; exit 1'"])
    assert rc == 0
    coll = json.loads((ws / "output/poc_validation/collected_results.json").read_text())["results"][0]
    assert coll["command_exit_code"] == 1
    assert coll["test_status"] in ("failed", "error")
    # and the validator marks a finding with that failing run as failed
    _inv(ws, [_cand("F10")])
    _run(validate, [])
    assert _results(ws)["F10"]["validation_status"] == "failed"


def test_invalid_reviewer_note_is_ignored(ws):
    _inv(ws, [_cand("F11")])
    _write(ws, "output/poc_validation/validation_notes/F11.json", {"finding_id": "F11"})  # missing required fields
    _run(validate, [])
    rep = json.loads((ws / "output/poc_validation/poc_validation_results.json").read_text())
    assert any("F11" in e for e in rep["schema_errors"])
    assert _results(ws)["F11"]["validation_status"] in ("inconclusive", "failed")
