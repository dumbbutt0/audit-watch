"""
P309 — coverage-completeness reporter + coverage-aware reach harness. No LLM, no network.

Verifies: coverage_percent/unexamined counts match a synthetic manifest+dispositions; the unexamined-file gap list
names the right files; complete iff every in-scope item is finding/cleared/deferred; research-only flags; and the
reach harness imports the reporter + exposes a `coverage` command. Production coverage scripts are NOT touched.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "research"))
ccr = importlib.import_module("coverage_completeness_report")


def _write(tmp, items, disp):
    out = tmp / "output"
    out.mkdir(parents=True, exist_ok=True)
    (out / "coverage_manifest.json").write_text(json.dumps({"items": items}))
    (out / "coverage_dispositions.json").write_text(json.dumps({"dispositions": disp}))
    return out


def _item(i, file, score=2, in_scope=True):
    return {"id": i, "kind": "function", "contract": "C", "name": i.split(":")[-1], "file": file,
            "attack_surface_score": score, "in_scope": in_scope}


def _disp(i, status, **kw):
    return dict({"manifest_id": i, "status": status}, **kw)


# 1. partial coverage: counts + per-file gap list + complete=False
def test_partial_coverage(tmp_path, monkeypatch):
    items = [_item("f:C:a", "src/A.sol"), _item("f:C:b", "src/A.sol", score=5),
             _item("f:C:c", "src/B.sol"), _item("f:C:d", "src/C.sol", in_scope=False)]
    disp = [_disp("f:C:a", "finding", finding_refs=["X-1"]), _disp("f:C:b", "unassigned"),
            _disp("f:C:c", "unassigned"), _disp("f:C:d", "deferred_out_of_scope", scope_reason="iface")]
    monkeypatch.setattr(ccr, "_audit_out", lambda t: _write(tmp_path, items, disp))
    r = ccr.coverage_report("t")
    assert r["in_scope"] == 3 and r["resolved"] == 1 and r["unexamined"] == 2
    assert r["coverage_percent"] == round(100 / 3, 1) and r["complete"] is False
    files = {u["file"] for u in r["unexamined_files"]}
    assert files == {"src/A.sol", "src/B.sol"}                      # the explicit gap list names the unread files
    # high-surface unexamined file sorts first (max_score 5 on A.sol)
    assert r["unexamined_files"][0]["file"] == "src/A.sol" and r["unexamined_files"][0]["max_score"] == 5
    assert r["research_only"] is True and r["is_gate"] is False and r["emits_findings"] is False


# 2. complete coverage: 100%, complete=True, no gaps
def test_complete_coverage(tmp_path, monkeypatch):
    items = [_item("f:C:a", "src/A.sol"), _item("f:C:b", "src/A.sol")]
    disp = [_disp("f:C:a", "finding", finding_refs=["X-1"]),
            _disp("f:C:b", "cleared", evidence=["A.sol:1"], clear_reason="guarded")]
    monkeypatch.setattr(ccr, "_audit_out", lambda t: _write(tmp_path, items, disp))
    r = ccr.coverage_report("t")
    assert r["coverage_percent"] == 100.0 and r["complete"] is True
    assert r["unexamined"] == 0 and r["unexamined_file_count"] == 0


# 3. an in-scope item with NO disposition record counts as unexamined (never silently dropped)
def test_missing_disposition_is_unexamined(tmp_path, monkeypatch):
    items = [_item("f:C:a", "src/A.sol")]
    monkeypatch.setattr(ccr, "_audit_out", lambda t: _write(tmp_path, items, []))
    r = ccr.coverage_report("t")
    assert r["unexamined"] == 1 and r["complete"] is False


# 4. reach harness wires in the reporter + exposes a `coverage` command (partial/complete labeling)
def test_reach_harness_is_coverage_aware():
    brt = importlib.import_module("blind_reach_test")
    assert hasattr(brt, "coverage") and brt.ccr is ccr


# 5. live predy: coverage report names the P308 missed-finding subsystems as unexamined (read-only)
def test_predy_gap_list_names_missed_subsystems():
    if not (ROOT / "audits/predy-2024-05-holdout/output/coverage_manifest.json").exists():
        pytest.skip("predy manifest not present")
    r = ccr.coverage_report("predy-2024-05-holdout")
    files = " ".join(u["file"] for u in r["unexamined_files"])
    assert r["complete"] is False and r["coverage_percent"] < 100
    # the P308 misses lived in these unread subsystems — now surfaced explicitly, not silent
    assert "GammaTradeMarket.sol" in files and "AddPairLogic.sol" in files and "PriceFeed.sol" in files
