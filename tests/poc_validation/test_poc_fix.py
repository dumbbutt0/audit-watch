"""
Tests for poc_fix.py — the per-finding fix router (deterministic, no LLM/network/forge).

poc-fix turns one fix-list item into the next concrete operator action: stages a /poc-validation bundle for
semantic actions, runs/templates a poc-collect command for log gaps, or prints targeted guidance for
downgrade/duplicate/reject. It never decides proof and never runs the skill. Mirrors tests/confirm style.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
poc_fix = importlib.import_module("poc_fix")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output" / "poc_validation").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _w(ws, rel, obj):
    p = ws / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2))
    return p


def _fixitem(fid, action, sev="High", bucket="missing_poc", **over):
    base = {"finding_id": fid, "title": f"{fid} t", "severity": sev, "current_bucket": bucket,
            "recommended_next_action": action, "why_blocked": "because", "exact_missing_requirements": ["x"],
            "test_file": None, "test_name": None, "raw_log_path": None, "validation_note_path": None,
            "shortest_next_step": "do it", "tier": 0, "proof_score": 0, "blocked": True, "manifest_refs": []}
    base.update(over)
    return base


def _setup(ws, items, *, mode="engagement", inv=None, vr=None, merged=None, findings=None):
    _w(ws, "output/poc_validation/fix_list.json",
       {"mode": mode, "total_items": len(items), "groups": {}, "ordered_items": items})
    _w(ws, "output/poc_validation/engagement_report.json",
       {"mode": mode, "findings": findings if findings is not None else
        [{"finding_id": it["finding_id"], "bucket": it["current_bucket"]} for it in items]})
    _w(ws, "output/poc_validation/poc_inventory.json", {"candidates": inv or []})
    _w(ws, "output/poc_validation/poc_validation_results.json", {"results": vr or []})
    _w(ws, "output/merged_findings.json", {"findings": merged or []})


def _run(argv):
    old = sys.argv
    sys.argv = ["poc_fix"] + argv
    try:
        return poc_fix.main()
    finally:
        sys.argv = old


def _session(ws, fid):
    return json.loads((ws / f"output/poc_validation/fix_sessions/{fid}.json").read_text())


# ---------------------------------------------------------------- tests

def test_missing_finding_id_exits_nonzero(ws):
    _setup(ws, [])
    assert _run([]) == 2


def test_unknown_finding_exits_nonzero(ws):
    _setup(ws, [_fixitem("A1", "write_missing_poc")])
    assert _run(["NOPE"]) == 2


def test_known_finding_creates_session(ws):
    _setup(ws, [_fixitem("A1", "write_missing_poc")],
           inv=[{"finding_id": "A1", "affected_functions": ["A.f"], "affected_files": ["src/A.sol"],
                 "manifest_refs": ["function:A:f#x"], "poc_required": True}])
    assert _run(["A1"]) == 0
    s = _session(ws, "A1")
    assert s["finding_id"] == "A1" and s["recommended_next_action"] == "write_missing_poc"
    assert (ws / "output/poc_validation/fix_sessions/A1.md").exists()


def test_write_missing_poc_next_step(ws):
    _setup(ws, [_fixitem("A2", "write_missing_poc")],
           inv=[{"finding_id": "A2", "affected_functions": ["A.f"], "poc_required": True,
                 "minimum_proof_goal": "prove it"}])
    _run(["A2"])
    s = _session(ws, "A2")
    assert "Write the PoC" in s["next_operator_step"]
    # bundle staged for /poc-validation context
    assert s["prepared_bundle_path"] == "output/poc_validation/bundles/A2.json"


def test_add_collected_log_without_command_prints_template(ws):
    _setup(ws, [_fixitem("A3", "add_collected_log", bucket="missing_collected_log",
                         test_file="test/A.t.sol", test_name="t")])
    _run(["A3"])
    s = _session(ws, "A3")
    assert any("poc-collect" in c for c in s["generated_commands"])
    # template only — nothing was executed
    assert not (ws / "output/poc_validation/collected_results.json").exists()


def test_add_collected_log_with_command_stages_collect(ws):
    _setup(ws, [_fixitem("A4", "add_collected_log", bucket="missing_collected_log",
                         test_file="test/A.t.sol", test_name="t")])
    # fake collector command — no forge needed
    assert _run(["A4", "--collect-command", "sh -c 'echo PASS'"]) == 0
    coll = json.loads((ws / "output/poc_validation/collected_results.json").read_text())
    assert coll["results"][0]["finding_id"] == "A4"
    s = _session(ws, "A4")
    assert any("[executed]" in c for c in s["generated_commands"])


def test_add_impact_assertion_prepares_bundle(ws):
    _setup(ws, [_fixitem("A5", "add_impact_assertion", bucket="needs_better_assertions")],
           inv=[{"finding_id": "A5", "poc_required": True, "affected_functions": ["A.f"]}])
    _run(["A5"])
    s = _session(ws, "A5")
    assert s["prepared_bundle_path"] == "output/poc_validation/bundles/A5.json"
    assert (ws / "output/poc_validation/bundles/A5.json").exists()
    assert any("post-state" in c for c in s["checklist"])
    assert "/poc-validation" in s["next_operator_step"]


def test_severity_overclaim_downgrade_guidance(ws):
    _setup(ws, [_fixitem("A6", "downgrade_severity", sev="High", bucket="severity_overclaim")],
           vr=[{"finding_id": "A6", "severity_supported": "Medium", "warnings": []}])
    _run(["A6"])
    s = _session(ws, "A6")
    assert "downgrade_severity" == s["recommended_next_action"]
    assert any("Medium" in d for d in s["details"])
    assert "Lower the finding's severity" in s["next_operator_step"]


def test_duplicate_merge_guidance(ws):
    _setup(ws, [_fixitem("A7", "resolve_duplicate", bucket="duplicate_proof")],
           merged=[{"id": "A7", "duplicate_of": "A1"}])
    _run(["A7"])
    s = _session(ws, "A7")
    assert any("A1" in d for d in s["details"])
    assert "duplicate" in s["next_operator_step"].lower()


def test_json_flag_prints_valid_json(ws, capsys):
    _setup(ws, [_fixitem("A8", "reject_poc", bucket="invalid_poc")])
    assert _run(["A8", "--json"]) == 0
    out = capsys.readouterr().out
    d = json.loads(out)
    assert d["finding_id"] == "A8" and d["recommended_next_action"] == "reject_poc"


def test_submission_ready_finding_is_noop(ws):
    _setup(ws, [], findings=[{"finding_id": "OK1", "bucket": "submission_ready"}])
    assert _run(["OK1"]) == 0  # nothing to fix, but not an error
    assert not (ws / "output/poc_validation/fix_sessions/OK1.json").exists()
