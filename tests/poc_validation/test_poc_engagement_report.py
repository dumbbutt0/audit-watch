"""
Tests for the PoC engagement report + dashboard status artifact — deterministic, no LLM/network/forge.

The report is the operator view: each PoC-required finding lands in exactly one bucket, the summary reconciles
with the buckets, and a small dashboard-facing status JSON is written for scripts/dashboard.py to surface.
Bucketing reuses poc_validation_gate.evaluate so it can never diverge from the gate. Mirrors tests/confirm style.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
report = importlib.import_module("poc_engagement_report")


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


def _cand(fid, sev="High", required=True, status="missing_poc"):
    return {"finding_id": fid, "title": f"{fid} t", "severity_ceiling": sev,
            "manifest_refs": ["function:A:f#x"], "affected_functions": ["A.f"], "affected_files": ["src/A.sol"],
            "poc_required": required, "required_proof_type": "unit", "status": status}


def _vr(fid, status="proven", sev="High", **over):
    base = {"finding_id": fid, "claimed_severity": sev, "validation_status": status, "proof_score": 80,
            "submission_ready": status == "proven", "recommended_next_action": "accept_for_submission",
            "failed_requirements": [], "warnings": [], "severity_supported": sev, "severity_overclaim": False,
            "limitations": "x", "test_file": "test/A.t.sol", "test_name": "t"}
    base.update(over)
    return base


def _setup(ws, cands, vrs=None, collected=None):
    _w(ws, "output/poc_validation/poc_inventory.json", {"candidates": cands})
    if vrs is not None:
        _w(ws, "output/poc_validation/poc_validation_results.json", {"results": vrs})
    if collected is not None:
        _w(ws, "output/poc_validation/collected_results.json", {"results": collected})


def _run(argv=None):
    old = sys.argv
    sys.argv = ["poc_engagement_report"] + (argv or [])
    try:
        return report.main()
    finally:
        sys.argv = old


def _report(ws):
    return json.loads((ws / "output/poc_validation/engagement_report.json").read_text())


def _bucket_of(rep, fid):
    return next(f["bucket"] for f in rep["findings"] if f["finding_id"] == fid)


def _fixlist(ws):
    return json.loads((ws / "output/poc_validation/fix_list.json").read_text())


def _dash(ws):
    return json.loads((ws / "output/dashboard/poc_validation_status.json").read_text())


# ---------------------------------------------------------------- mode + fix-list (Phase 6)

def test_mode_engagement_is_default(ws):
    _setup(ws, [_cand("D1", "High")], [])
    _run()
    assert _report(ws)["mode"] == "engagement"
    assert _dash(ws)["mode"] == "engagement"


def test_mode_submission_stricter_bucketing(ws):
    # Medium partially_proven WITHOUT limitations: passes engagement, fails submission.
    cand = [_cand("D2", "Medium")]
    vr = [_vr("D2", "partially_proven", "Medium", submission_ready=False, limitations="",
              recommended_next_action="mark_inconclusive")]
    coll = [{"finding_id": "D2", "test_file": "t", "command_exit_code": 0, "raw_result_path": "x"}]
    _setup(ws, cand, vr, coll)
    _run(["--mode", "engagement"])
    assert _bucket_of(_report(ws), "D2") == "engagement_ready_but_not_submission_ready"
    _run(["--mode", "submission"])
    # in submission mode it falls through to its specific gap bucket (no longer "engagement_ready")
    assert _bucket_of(_report(ws), "D2") != "engagement_ready_but_not_submission_ready"
    assert _report(ws)["mode"] == "submission"


def test_fix_list_written_and_grouped(ws):
    _setup(ws, [_cand("F1", "High"), _cand("F2", "Medium")], [])  # both missing_poc
    _run()
    assert (ws / "output/poc_validation/fix_list.md").exists()
    fl = _fixlist(ws)
    assert fl["total_items"] == 2
    assert "write_missing_poc" in fl["groups"]
    assert {i["finding_id"] for i in fl["groups"]["write_missing_poc"]} == {"F1", "F2"}
    # every fix item carries the required fields
    for it in fl["ordered_items"]:
        for k in ("finding_id", "title", "severity", "current_bucket", "recommended_next_action",
                  "why_blocked", "exact_missing_requirements", "shortest_next_step"):
            assert k in it, k


def test_high_critical_blockers_sort_first(ws):
    _setup(ws, [_cand("MED", "Medium"), _cand("HI", "High")], [])  # both missing_poc -> tier 0/1 by severity
    _run()
    ordered = _fixlist(ws)["ordered_items"]
    assert ordered[0]["finding_id"] == "HI" and ordered[0]["tier"] == 0
    assert ordered[1]["finding_id"] == "MED" and ordered[1]["tier"] == 1


def test_dashboard_has_new_fields(ws):
    _setup(ws, [_cand("X1", "High")], [_vr("X1", "setup_only", "High", submission_ready=False)],
           [{"finding_id": "X1", "test_file": "t", "command_exit_code": 0, "raw_result_path": "x"}])
    _run()
    d = _dash(ws)
    for k in ("mode", "fix_list_path", "top_fix_items", "submission_blockers", "closest_to_ready"):
        assert k in d, k
    assert d["fix_list_path"].endswith("fix_list.md")
    # setup_only finding is a submission blocker and gets remove_invalid_setup
    assert any(b["finding_id"] == "X1" for b in d["submission_blockers"])
    assert any(i["recommended_next_action"] == "remove_invalid_setup" for i in d["top_fix_items"])


def test_mock_fixture_is_valid_json():
    p = Path(__file__).resolve().parents[2] / "dashboard" / "mock_data" / "poc_validation_status.json"
    assert p.exists()
    d = json.loads(p.read_text())
    assert "summary" in d and "buckets" in d and d["mode"] in ("engagement", "submission")
    # covers the illustrative states the request asks for
    assert d["buckets"]["submission_ready"] and d["buckets"]["missing_poc"]
    assert d["buckets"]["needs_negative_control"] and d["buckets"]["severity_overclaim"]
    assert d["buckets"]["setup_only"]


# ---------------------------------------------------------------- bucket tests

def test_proven_high_is_submission_ready(ws):
    _setup(ws, [_cand("A1", "High")], [_vr("A1", "proven", "High")],
           [{"finding_id": "A1", "test_file": "test/A.t.sol", "test_name": "t", "command_exit_code": 0,
             "raw_result_path": "x.log"}])
    _run()
    assert _bucket_of(_report(ws), "A1") == "submission_ready"


def test_partial_medium_no_limits_is_engagement_not_submission(ws):
    _setup(ws, [_cand("A2", "Medium")],
           [_vr("A2", "partially_proven", "Medium", submission_ready=False, limitations="")],
           [{"finding_id": "A2", "test_file": "test/A.t.sol", "command_exit_code": 0, "raw_result_path": "x.log"}])
    _run()
    assert _bucket_of(_report(ws), "A2") == "engagement_ready_but_not_submission_ready"


def test_missing_poc(ws):
    _setup(ws, [_cand("A3", "High")], [])
    _run()
    assert _bucket_of(_report(ws), "A3") == "missing_poc"


def test_missing_collected_log(ws):
    # validator knows a test_file but there is no collected run/log
    _setup(ws, [_cand("A4", "High")],
           [_vr("A4", "inconclusive", "High", submission_ready=False, test_file="test/A.t.sol")])
    _run()
    assert _bucket_of(_report(ws), "A4") == "missing_collected_log"


def test_setup_only(ws):
    _setup(ws, [_cand("A5", "High")],
           [_vr("A5", "setup_only", "High", submission_ready=False)],
           [{"finding_id": "A5", "test_file": "test/A.t.sol", "command_exit_code": 0, "raw_result_path": "x.log"}])
    _run()
    assert _bucket_of(_report(ws), "A5") == "setup_only"


def test_severity_overclaim(ws):
    _setup(ws, [_cand("A6", "High")],
           [_vr("A6", "proven", "High", severity_overclaim=True, severity_supported="Low")],
           [{"finding_id": "A6", "test_file": "test/A.t.sol", "command_exit_code": 0, "raw_result_path": "x.log"}])
    _run()
    assert _bucket_of(_report(ws), "A6") == "severity_overclaim"


def test_duplicate_proof(ws):
    _setup(ws, [_cand("A7", "Medium")],
           [_vr("A7", "duplicate_proof", "Medium", submission_ready=False)],
           [{"finding_id": "A7", "test_file": "test/A.t.sol", "command_exit_code": 0, "raw_result_path": "x.log"}])
    _run()
    assert _bucket_of(_report(ws), "A7") == "duplicate_proof"


def test_eval_only_not_required(ws):
    _setup(ws, [_cand("A8", "Low", required=False, status="not_required_eval_only")], [])
    _run()
    assert _bucket_of(_report(ws), "A8") == "eval_only_not_required"


def test_needs_negative_control(ws):
    _setup(ws, [_cand("A9", "Medium")],
           [_vr("A9", "partially_proven", "Medium", submission_ready=False, limitations="",
                recommended_next_action="add_negative_control", warnings=["no_negative_control_detected"])],
           [{"finding_id": "A9", "test_file": "test/A.t.sol", "command_exit_code": 0, "raw_result_path": "x.log"}])
    _run()
    # passes engagement (Medium partial) -> engagement bucket wins over needs_* (gate-authoritative)
    b = _bucket_of(_report(ws), "A9")
    assert b in ("engagement_ready_but_not_submission_ready", "needs_negative_control")


# ---------------------------------------------------------------- summary + dashboard

def test_summary_reconciles_and_dashboard_written(ws):
    cands = [_cand("H1", "High"), _cand("M1", "Medium"), _cand("E1", "Low", required=False,
             status="not_required_eval_only")]
    vrs = [_vr("H1", "proven", "High"), _vr("M1", "partially_proven", "Medium", submission_ready=False,
                                            limitations="")]
    coll = [{"finding_id": "H1", "test_file": "t", "command_exit_code": 0, "raw_result_path": "x"},
            {"finding_id": "M1", "test_file": "t", "command_exit_code": 0, "raw_result_path": "x"}]
    _setup(ws, cands, vrs, coll)
    _run()
    rep = _report(ws)
    # every finding is in exactly one bucket; buckets reconcile with finding count
    assert sum(len(v) for v in rep["buckets"].values()) == len(rep["findings"]) == 3
    m = rep["metrics"]
    assert m["total_findings_needing_poc"] == 2  # H1 + M1 (E1 is eval-only)
    assert m["submission_ready"] == len(rep["buckets"]["submission_ready"])
    # dashboard artifact exists with required summary + bucket fields
    dash = json.loads((ws / "output/dashboard/poc_validation_status.json").read_text())
    for k in ("total_findings_needing_poc", "submission_ready", "engagement_ready", "missing_poc",
              "missing_collected_log", "invalid_or_setup_only", "severity_overclaim",
              "high_critical_blocked", "medium_blocked"):
        assert k in dash["summary"], k
    for b in ("submission_ready", "engagement_ready_but_not_submission_ready", "missing_poc",
              "eval_only_not_required"):
        assert b in dash["buckets"], b
    assert "top_next_actions" in dash and "blocking_items" in dash and "stale_or_missing_inputs" in dash


def test_dashboard_reads_poc_validation_without_crashing(ws):
    pytest.importorskip("fastapi")
    dashboard = importlib.import_module("dashboard")
    # artifact absent -> graceful {}
    st = dashboard._build_state()
    assert st.get("poc_validation") == {}
    # artifact present -> surfaced
    _setup(ws, [_cand("H1", "High")], [_vr("H1", "proven", "High")],
           [{"finding_id": "H1", "test_file": "t", "command_exit_code": 0, "raw_result_path": "x"}])
    _run()
    st2 = dashboard._build_state()
    assert "summary" in st2["poc_validation"]
