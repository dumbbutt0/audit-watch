"""
Task 5 — cumulative deep-pass ledger. The ledger must record CUMULATIVE history (every item ever queued/
executed/waived/skipped) so an item executed in a later run still shows as executed even after it leaves the
current queue (Revert Lend's misleading "executed 0"). Post-freeze, the scorer can stamp answer_key_matched.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
ledger = importlib.import_module("deep_pass_ledger")
annotate = importlib.import_module("annotate_ledger_answer_key")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    (tmp_path / "output" / "eval_ready").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    return tmp_path


def _it(mid, name="liquidate"):
    return {"id": mid, "kind": "function", "contract": "V", "name": name, "in_scope": True,
            "attack_surface_score": 4, "tags": [], "source_span": {}}


def _queue(ws, item_ids, tier=3):
    (ws / "output" / "deep_pass_queue.json").write_text(json.dumps({"clusters": [
        {"cluster_id": "DPQ-x-V", "priority_tier": tier, "tier_reason": "liq", "suggested_specialist": "logic",
         "item_ids": item_ids}]}))


def _manifest(ws, items):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "source": {}, "items": items}))


def _disp(ws, statuses):
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps(
        {"dispositions": [{"manifest_id": m, "status": s, "assigned_pass": "deep"} for m, s in statuses.items()]}))


def _run():
    old = sys.argv
    sys.argv = ["deep_pass_ledger", "--quiet"]
    try:
        return ledger.main()
    finally:
        sys.argv = old


def test_cumulative_history_survives_queue_rebuild(ws):
    a, b = "function:V:liquidate#1", "function:V:getValue#2"
    _manifest(ws, [_it(a, "liquidate"), _it(b, "getValue")])
    # run 1: both queued + pending
    _queue(ws, [a, b]); _disp(ws, {a: "assigned", b: "assigned"})
    _run()
    # run 2: a executed (cleared) and DROPS OUT of the rebuilt queue; only b remains queued
    _disp(ws, {a: "cleared", b: "assigned"})
    _queue(ws, [b])
    _run()
    hist = [json.loads(l) for l in (ws / "output" / "deep_pass_ledger_history.jsonl").read_text().splitlines() if l.strip()]
    run_ids = {h["run_id"] for h in hist}
    assert len(run_ids) == 2                              # two distinct runs appended
    cum = json.loads((ws / "output" / "deep_pass_cumulative.json").read_text())
    by_id = {i["manifest_id"]: i for i in cum["items"]}
    assert by_id[a]["latest_type"] == "executed"         # executed shown even though a left the queue
    assert by_id[b]["latest_type"] == "skipped"
    assert cum["cumulative_tier12_completion_rate"] is not None


def test_annotate_answer_key_post_freeze(ws):
    a = "function:V:liquidate#1"
    _manifest(ws, [_it(a)]); _queue(ws, [a]); _disp(ws, {a: "assigned"})
    _run()
    (ws / "output" / "eval_ready" / "ledger_answer_key_matches.json").write_text(
        json.dumps({"matched_manifest_ids": [a]}))
    old = sys.argv
    sys.argv = ["annotate_ledger_answer_key"]
    try:
        assert annotate.main() == 0
    finally:
        sys.argv = old
    cum = json.loads((ws / "output" / "deep_pass_cumulative.json").read_text())
    assert cum["answer_key_matched_total"] == 1
    assert a in cum["skipped_or_waived_that_were_real"]   # we skipped an item that was a real finding
