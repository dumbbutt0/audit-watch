"""
Tests for the /poc-validation skill triplet I/O (prepare + write) — deterministic, no LLM/network/forge.

prepare packages context bundles; the skill (out of band) writes per-finding reviewer notes; write normalizes
them into schema-valid validation_notes; validate_poc.py remains the source of truth and only ever downgrades.
Mirrors tests/confirm style.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
prepare = importlib.import_module("poc_validation_prepare")
write = importlib.import_module("poc_validation_write")
validate = importlib.import_module("validate_poc")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output" / "poc_validation").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _w(ws, rel, obj):
    p = ws / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) if not isinstance(obj, str) else obj)
    return p


def _cand(fid, sev="High", status="missing_poc"):
    return {"finding_id": fid, "title": f"{fid} drains funds", "severity_ceiling": sev,
            "source": "merged_findings", "manifest_refs": ["function:A:f#x"], "affected_functions": ["A.f"],
            "affected_files": ["src/A.sol"], "poc_required": True, "required_proof_type": "unit",
            "required_attacker_entrypoint": "A.f", "required_impact_assertion": "balance drop", "status": status}


def _inv(ws, cands):
    _w(ws, "output/poc_validation/poc_inventory.json", {"candidates": cands})


def _skill_out(fid, **over):
    base = {"finding_id": fid, "root_cause_proven": True, "attacker_reachability_proven": True,
            "impact_proven": True, "state_transition_proven": True, "severity_supported": "High",
            "why_test_proves_claim": "EOA calls A.f; victim balance 100 -> 0", "limitations": "one block",
            "test_file": "test/A.t.sol", "test_name": "test_drain", "command_exit_code": 0,
            "recommended_validation_status": "proven"}
    base.update(over)
    return base


GOOD_TEST = ("contract T is Test {\n  function test_drain() public {\n"
             "    uint256 pre = token.balanceOf(victim);\n    vm.prank(attacker); target.f();\n"
             "    assertEq(token.balanceOf(victim), 0);\n  }\n  // negative_control here\n}\n")


def _run(mod, argv):
    old = sys.argv
    sys.argv = [mod.__name__] + argv
    try:
        return mod.main()
    finally:
        sys.argv = old


def _notes(ws, fid):
    return json.loads((ws / f"output/poc_validation/validation_notes/{fid}.json").read_text())


def _results(ws):
    return {r["finding_id"]: r for r in
            json.loads((ws / "output/poc_validation/poc_validation_results.json").read_text())["results"]}


# ---------------------------------------------------------------- prepare

def test_prepare_creates_bundle_for_unvalidated_poc(ws):
    _inv(ws, [_cand("P1")])
    assert _run(prepare, []) == 0
    idx = json.loads((ws / "output/poc_validation/bundles/index.json").read_text())
    assert idx["written"] == 1
    b = json.loads((ws / "output/poc_validation/bundles/P1.json").read_text())
    assert b["finding_id"] == "P1" and b["severity"] == "High"
    assert "skill_outputs/P1.json" in b["prompt_instructions"]


def test_prepare_includes_source_test_log_excerpts(ws):
    _inv(ws, [_cand("P2")])
    _w(ws, "src/A.sol", "// SPDX\ncontract A { function f() external { selfdestruct(payable(msg.sender)); } }\n")
    _w(ws, "test/A.t.sol", GOOD_TEST)
    _w(ws, "output/merged_findings.json",
       {"findings": [{"id": "P2", "location": {"file": "src/A.sol", "function": "f", "lines": "2"}}]})
    _w(ws, "output/poc_validation/collected_results.json",
       {"results": [{"finding_id": "P2", "test_file": "test/A.t.sol", "test_name": "test_drain",
                     "command": "forge test", "command_exit_code": 0, "raw_result_path": "x.log"}]})
    _run(prepare, [])
    b = json.loads((ws / "output/poc_validation/bundles/P2.json").read_text())
    assert "selfdestruct" in b["source_excerpt"]
    assert "test_drain" in b["test_excerpt"]
    assert b["test_file"] == "test/A.t.sol"


def test_prepare_overwrite_flag(ws):
    _inv(ws, [_cand("P3")])
    _run(prepare, [])
    _run(prepare, [])  # second run without --overwrite skips
    idx = json.loads((ws / "output/poc_validation/bundles/index.json").read_text())
    assert idx["skipped_existing"] == 1
    assert _run(prepare, ["--overwrite"]) == 0
    idx = json.loads((ws / "output/poc_validation/bundles/index.json").read_text())
    assert idx["written"] == 1


# ---------------------------------------------------------------- write

def test_write_accepts_valid_skill_output(ws):
    _inv(ws, [_cand("W1")])
    _w(ws, "output/poc_validation/skill_outputs/W1.json", _skill_out("W1"))
    assert _run(write, []) == 0
    note = _notes(ws, "W1")
    assert note["finding_id"] == "W1"
    assert note["validation_status"] == "proven"
    assert note["root_cause_proven"] is True


def test_write_rejects_missing_finding_id(ws):
    _inv(ws, [_cand("W2")])
    _w(ws, "output/poc_validation/skill_outputs/bad.json", {"root_cause_proven": True})
    _run(write, [])
    summ = json.loads((ws / "output/poc_validation/poc_validation_write_summary.json").read_text())
    assert summ["applied"] == 0
    assert any("missing finding_id" in r for r in summ["rejected_reasons"])


def test_write_rejects_unknown_finding_id_by_default(ws):
    _inv(ws, [_cand("W3")])
    _w(ws, "output/poc_validation/skill_outputs/UNKNOWN.json", _skill_out("UNKNOWN"))
    _run(write, [])
    summ = json.loads((ws / "output/poc_validation/poc_validation_write_summary.json").read_text())
    assert summ["applied"] == 0 and any("not in inventory" in r for r in summ["rejected_reasons"])
    # accepted with --allow-unknown
    assert _run(write, ["--allow-unknown"]) == 0
    assert (ws / "output/poc_validation/validation_notes/UNKNOWN.json").exists()


def test_write_normalizes_recommended_status(ws):
    _inv(ws, [_cand("W4")])
    _w(ws, "output/poc_validation/skill_outputs/W4.json",
       _skill_out("W4", recommended_validation_status="needs_negative_control", impact_proven=False))
    _run(write, [])
    note = _notes(ws, "W4")
    assert note["validation_status"] == "partially_proven"  # mapped from needs_negative_control
    assert "needs_negative_control" in note["reviewer_notes"]


def test_write_summary_generated(ws):
    _inv(ws, [_cand("W5")])
    _w(ws, "output/poc_validation/skill_outputs/W5.json", _skill_out("W5"))
    _run(write, [])
    summ = json.loads((ws / "output/poc_validation/poc_validation_write_summary.json").read_text())
    assert summ["applied"] == 1 and "generated_at" in summ


# ---------------------------------------------------------------- end-to-end with validator

def test_validate_consumes_written_notes_proven(ws):
    _inv(ws, [_cand("E1")])
    _w(ws, "test/A.t.sol", GOOD_TEST)
    _w(ws, "output/poc_validation/skill_outputs/E1.json", _skill_out("E1"))
    _w(ws, "output/poc_validation/collected_results.json",
       {"results": [{"finding_id": "E1", "test_file": "test/A.t.sol", "test_name": "test_drain",
                     "command_exit_code": 0}]})
    _run(write, [])
    _run(validate, [])
    assert _results(ws)["E1"]["validation_status"] == "proven"


def test_validate_downgrades_overclaim_from_notes(ws):
    _inv(ws, [_cand("E2", sev="High")])
    _w(ws, "test/A.t.sol", GOOD_TEST)
    _w(ws, "output/poc_validation/skill_outputs/E2.json", _skill_out("E2", severity_supported="Low"))
    _w(ws, "output/poc_validation/collected_results.json",
       {"results": [{"finding_id": "E2", "test_file": "test/A.t.sol", "test_name": "test_drain",
                     "command_exit_code": 0}]})
    _run(write, [])
    _run(validate, [])
    r = _results(ws)["E2"]
    assert r["severity_overclaim"] is True and r["submission_ready"] is False


def test_check_api_free_remains_green(ws, monkeypatch):
    # the new optional skill entry must keep the critical-path api-free check green
    caf = importlib.import_module("check_api_free")
    rc = caf.main() if hasattr(caf, "main") else 0
    assert rc == 0
