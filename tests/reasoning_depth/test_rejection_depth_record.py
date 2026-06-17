"""
P245 #4 — rejection depth-record enforcement regression tests (default-off).

Drives the real triage_write.main() against a tmp workspace. Covers: sensitive rejection without a
depth record -> rerouted to human queue; sensitive rejection with a complete record -> stays rejected;
non-sensitive rejection unaffected; default-off preserves the existing workflow.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
rdu = importlib.import_module("reasoning_depth_utils")
tw = importlib.import_module("triage_write")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "data" / "triage" / "_bundles").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _decision(fid, status="rejected", **extra):
    d = {"finding_id": fid, "triage_status": status, "recommended_severity": "Medium",
         "decision_reason": "looks mitigated"}
    d.update(extra)
    return d


def _run(ws, monkeypatch, decisions, bundle_index=None, enforced=True):
    dec_path = ws / "data" / "triage" / "_decisions.json"
    dec_path.write_text(json.dumps({"decisions": decisions}))
    if bundle_index is not None:
        (ws / "data" / "triage" / "_bundles" / "index.json").write_text(json.dumps(bundle_index))
    monkeypatch.setattr(tw, "_rejection_depth_enforced", lambda: enforced)
    monkeypatch.setattr(sys, "argv", ["triage_write.py", "--decisions", str(dec_path)])
    rc = tw.main()
    assert rc == 0
    hq = ws / "data" / "triage" / "human_review_queue.jsonl"
    queue = [json.loads(l) for l in hq.read_text().splitlines()] if hq.exists() else []
    rejected = ws / "data" / "triage" / "rejected.jsonl"
    rej = [json.loads(l) for l in rejected.read_text().splitlines()] if rejected.exists() else []
    return queue, rej


def test_complete_depth_fields_constant():
    assert set(rdu.DEPTH_FIELDS) == {"source_anchors", "defense_anchors", "attacker_path",
                                     "impact_path", "state_timeline", "defense_fully_covers_reason"}


def test_sensitive_rejection_without_depth_record_rerouted(ws, monkeypatch):
    bundle = [{"finding_id": "OR-001",
               "title": "oracle staleness: getPrice ignores updatedAt / heartbeat", "safety_net": False}]
    queue, rej = _run(ws, monkeypatch, [_decision("OR-001")], bundle, enforced=True)
    assert any(r["finding_id"] == "OR-001" and r.get("needs_depth") for r in queue)
    assert "oracle freshness" in str(queue)
    assert not any(r["finding_id"] == "OR-001" for r in rej)  # not silently rejected


def test_sensitive_rejection_with_complete_record_allowed(ws, monkeypatch):
    bundle = [{"finding_id": "OR-002", "title": "oracle staleness in price feed", "safety_net": False}]
    dec = _decision("OR-002", depth_record={k: "x" for k in rdu.DEPTH_FIELDS})
    queue, rej = _run(ws, monkeypatch, [dec], bundle, enforced=True)
    assert any(r["finding_id"] == "OR-002" for r in rej)             # stays rejected
    assert not any(r.get("finding_id") == "OR-002" for r in queue)   # not rerouted


def test_non_sensitive_rejection_unaffected(ws, monkeypatch):
    bundle = [{"finding_id": "GA-001", "title": "gas: cache array length in loop", "safety_net": False}]
    queue, rej = _run(ws, monkeypatch, [_decision("GA-001")], bundle, enforced=True)
    assert any(r["finding_id"] == "GA-001" for r in rej)
    assert not any(r.get("finding_id") == "GA-001" for r in queue)


def test_default_off_preserves_workflow(ws, monkeypatch):
    """Flag OFF: even a sensitive rejection with no depth record is accepted as before."""
    bundle = [{"finding_id": "LQ-001", "title": "liquidation bypass via health factor", "safety_net": False}]
    queue, rej = _run(ws, monkeypatch, [_decision("LQ-001")], bundle, enforced=False)
    assert any(r["finding_id"] == "LQ-001" for r in rej)
    assert not any(r.get("finding_id") == "LQ-001" for r in queue)
