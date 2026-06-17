"""
Tests for poc_fix_all.py — the batch PoC-fix driver (deterministic, no LLM/network/forge).

poc-fix-all walks the fix-list in priority order, stages a fix session per actionable finding, and writes a
consolidated operator worklist. It stages safely: never executes test commands, records per-item failures and
continues, and skips existing sessions unless --overwrite. Mirrors tests/confirm style.
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
poc_fix_all = importlib.import_module("poc_fix_all")


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


def _item(fid, action, sev="High", bucket="missing_poc", blocked=True, proof=0):
    return {"finding_id": fid, "title": f"{fid} t", "severity": sev, "current_bucket": bucket,
            "recommended_next_action": action, "why_blocked": "because", "exact_missing_requirements": ["x"],
            "test_file": None, "test_name": None, "raw_log_path": None, "validation_note_path": None,
            "shortest_next_step": "do it", "tier": 0, "proof_score": proof, "blocked": blocked, "manifest_refs": []}


def _setup(ws, items, *, mode="engagement", inv=None, findings=None):
    _w(ws, "output/poc_validation/fix_list.json",
       {"mode": mode, "total_items": len(items), "groups": {}, "ordered_items": items})
    _w(ws, "output/poc_validation/engagement_report.json",
       {"mode": mode, "findings": findings if findings is not None else
        [{"finding_id": it["finding_id"], "bucket": it["current_bucket"], "severity": it["severity"]} for it in items]})
    _w(ws, "output/poc_validation/poc_inventory.json", {"candidates": inv or []})
    _w(ws, "output/poc_validation/poc_validation_results.json", {"results": []})
    _w(ws, "output/merged_findings.json", {"findings": []})


def _run(argv=None):
    old = sys.argv
    sys.argv = ["poc_fix_all"] + (argv or [])
    try:
        return poc_fix_all.main()
    finally:
        sys.argv = old


def _wl(ws):
    return json.loads((ws / "output/poc_validation/operator_worklist.json").read_text())


# ---------------------------------------------------------------- tests

def test_default_processes_non_ready_and_writes_worklist(ws):
    _setup(ws, [_item("A1", "downgrade_severity", "High", "severity_overclaim"),
                _item("A2", "resolve_duplicate", "Medium", "duplicate_proof", blocked=False)])
    assert _run(["--quiet"]) == 0
    assert (ws / "output/poc_validation/operator_worklist.md").exists()
    wl = _wl(ws)
    assert wl["total"] == 2 and wl["staged"] == 2
    assert {i["finding_id"] for i in wl["items"]} == {"A1", "A2"}


def test_limit_caps_items(ws):
    _setup(ws, [_item(f"A{i}", "reject_poc", "Low", "invalid_poc", blocked=False) for i in range(5)])
    _run(["--limit", "2", "--quiet"])
    assert _wl(ws)["total"] == 2


def test_actions_filter(ws):
    _setup(ws, [_item("A1", "downgrade_severity", "High", "severity_overclaim"),
                _item("A2", "reject_poc", "High", "invalid_poc")])
    _run(["--actions", "reject_poc", "--quiet"])
    wl = _wl(ws)
    assert wl["total"] == 1 and wl["items"][0]["finding_id"] == "A2"


def test_severity_filter(ws):
    _setup(ws, [_item("HI", "reject_poc", "High", "invalid_poc"),
                _item("LO", "reject_poc", "Low", "invalid_poc", blocked=False)])
    _run(["--severity", "High", "--quiet"])
    wl = _wl(ws)
    assert wl["total"] == 1 and wl["items"][0]["finding_id"] == "HI"


def test_high_critical_ranked_first(ws):
    _setup(ws, [_item("MED", "reject_poc", "Medium", "invalid_poc"),
                _item("HI", "downgrade_severity", "High", "severity_overclaim")])
    _run(["--quiet"])
    items = _wl(ws)["items"]
    assert items[0]["finding_id"] == "HI" and items[0]["rank"] == 1


def test_existing_sessions_skipped_unless_overwrite(ws):
    _setup(ws, [_item("A1", "reject_poc", "High", "invalid_poc")])
    _w(ws, "output/poc_validation/fix_sessions/A1.json", {"finding_id": "A1", "recommended_next_action": "reject_poc"})
    _run(["--quiet"])
    assert _wl(ws)["items"][0]["status"] == "skipped"
    _run(["--overwrite", "--quiet"])
    assert _wl(ws)["items"][0]["status"] == "staged"


def test_failure_does_not_stop_batch(ws, monkeypatch):
    _setup(ws, [_item("BOOM", "reject_poc", "High", "invalid_poc"),
                _item("OK", "reject_poc", "Medium", "invalid_poc")])
    real = poc_fix.process_finding

    def flaky(fid, *a, **k):
        if fid == "BOOM":
            raise RuntimeError("staging blew up")
        return real(fid, *a, **k)
    monkeypatch.setattr(poc_fix, "process_finding", flaky)
    assert _run(["--quiet"]) == 0
    wl = _wl(ws)
    assert wl["failed"] == 1 and wl["staged"] == 1
    assert {i["finding_id"]: i["status"] for i in wl["items"]} == {"BOOM": "failed", "OK": "staged"}


def test_run_collect_executes_nothing(ws):
    _setup(ws, [_item("A1", "add_collected_log", "High", "missing_collected_log")])
    _run(["--run-collect", "--quiet"])
    # the batch never invents a command, so nothing is executed/recorded
    assert not (ws / "output/poc_validation/collected_results.json").exists()


def test_json_prints_valid_json(ws, capsys):
    _setup(ws, [_item("A1", "reject_poc", "High", "invalid_poc")])
    assert _run(["--json"]) == 0
    d = json.loads(capsys.readouterr().out)
    assert d["total"] == 1 and d["items"][0]["finding_id"] == "A1"


def test_bundle_staged_items_marked_ready(ws):
    _setup(ws, [_item("A1", "add_impact_assertion", "High", "needs_better_assertions")],
           inv=[{"finding_id": "A1", "poc_required": True, "affected_functions": ["A.f"]}])
    _run(["--quiet"])
    item = _wl(ws)["items"][0]
    assert item["ready_for_poc_validation"] is True
    assert item["prepared_bundle_path"] == "output/poc_validation/bundles/A1.json"


def test_include_ready_lists_submission_ready(ws):
    _setup(ws, [_item("A1", "reject_poc", "High", "invalid_poc")],
           findings=[{"finding_id": "A1", "bucket": "invalid_poc", "severity": "High"},
                     {"finding_id": "OK1", "bucket": "submission_ready", "severity": "Medium"}])
    _run(["--include-ready", "--quiet"])
    wl = _wl(ws)
    ready = [i for i in wl["items"] if i["status"] == "ready"]
    assert ready and ready[0]["finding_id"] == "OK1"
