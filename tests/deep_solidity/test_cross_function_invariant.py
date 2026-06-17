"""
Cross-function / boundary invariant lens (Recall H-03/H-04/H-06/H-07). Detects candidate writer/reader
mismatches; safe-equivalent shapes are not flagged. Code embedded in the `signature` field + --no-source.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
cfi = importlib.import_module("cross_function_invariant_taxonomy")
audit = importlib.import_module("cross_function_invariant_audit")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _item(contract, name, sig, mid=None):
    return {"id": mid or f"function:{contract}:{name}#0001", "kind": "function", "contract": contract,
            "file": f"{contract}.sol", "name": name, "signature": sig, "in_scope": True,
            "attack_surface_score": 3, "tags": [], "source_span": {}}


def _write_manifest(ws, items):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "source": {}, "items": items}))
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps({"dispositions": []}))


def _run():
    old = sys.argv
    sys.argv = ["cross_function_invariant_audit", "--no-source"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old


def _report(ws):
    return json.loads((ws / "output" / "cross_function_invariant_audit.json").read_text())


# ---------- taxonomy unit ----------

def test_key_calls_extracted():
    c = cfi.classify("commit", snippet="s_postbox[toHash(e)] = e.data;")
    assert c["key_calls"] == ["tohash"] and c["has_shared_state"]


# ---------- H-03 store-key vs read-key ----------

def test_h03_hash_mismatch_detected(ws):
    _write_manifest(ws, [
        _item("Postbox", "commitMessage", "function commitMessage(Env e){ s.postbox[toHash(e)] = e.data; }", "function:Postbox:commitMessage#01"),
        _item("Postbox", "consumeMessage", "function consumeMessage(Env e){ return s.postbox[toTracingId(e)]; }", "function:Postbox:consumeMessage#02"),
    ])
    _run()
    fams = {h["family"] for h in _report(ws)["detected"]}
    assert "store_key_vs_read_key_divergence" in fams


def test_h03_safe_same_key_not_flagged(ws):
    _write_manifest(ws, [
        _item("Postbox", "commitMessage", "function commitMessage(Env e){ s.postbox[toHash(e)] = e.data; }", "function:Postbox:commitMessage#01"),
        _item("Postbox", "consumeMessage", "function consumeMessage(Env e){ return s.postbox[toHash(e)]; }", "function:Postbox:consumeMessage#02"),
    ])
    _run()
    fams = {h["family"] for h in _report(ws)["detected"]}
    assert "store_key_vs_read_key_divergence" not in fams


# ---------- H-04 counter / limit divergence ----------

def test_h04_batch_overflow_detected(ws):
    _write_manifest(ws, [
        _item("Gateway", "commitBottomUpMsg", "function commitBottomUpMsg(bytes m) external { batchMsgCount += 1; }", "function:Gateway:commitBottomUpMsg#01"),
        _item("SubnetCheckpointing", "ensureValidCheckpoint", "function ensureValidCheckpoint(uint64 n) view { require(n <= maxMsgsPerBatch); }", "function:SubnetCheckpointing:ensureValidCheckpoint#02"),
    ])
    _run()
    fams = {h["family"] for h in _report(ws)["detected"]}
    assert "counter_limit_divergence" in fams


def test_h04_safe_local_bound_not_flagged(ws):
    _write_manifest(ws, [
        _item("Gateway", "commitBottomUpMsg", "function commitBottomUpMsg(bytes m) external { require(batchMsgCount < maxMsgsPerBatch); batchMsgCount += 1; }", "function:Gateway:commitBottomUpMsg#01"),
    ])
    _run()
    fams = {h["family"] for h in _report(ws)["detected"]}
    assert "counter_limit_divergence" not in fams


# ---------- H-06 cross-function reentrancy ----------

def test_h06_cross_function_reentrancy_detected(ws):
    _write_manifest(ws, [
        _item("SubnetActor", "leave", "function leave() external nonReentrant { collateral[msg.sender]=0; payable(msg.sender).transfer(amount); }", "function:SubnetActor:leave#01"),
        _item("SubnetActor", "addBootstrap", "function addBootstrap(string a) external { bootstrapNodes[msg.sender]=a; }", "function:SubnetActor:addBootstrap#02"),
    ])
    _run()
    fams = {h["family"] for h in _report(ws)["detected"]}
    assert "cross_function_reentrancy" in fams


def test_h06_safe_all_guarded_not_flagged(ws):
    _write_manifest(ws, [
        _item("SubnetActor", "leave", "function leave() external nonReentrant { collateral[msg.sender]=0; payable(msg.sender).transfer(amount); }", "function:SubnetActor:leave#01"),
        _item("SubnetActor", "addBootstrap", "function addBootstrap(string a) external nonReentrant { bootstrapNodes[msg.sender]=a; }", "function:SubnetActor:addBootstrap#02"),
    ])
    _run()
    fams = {h["family"] for h in _report(ws)["detected"]}
    assert "cross_function_reentrancy" not in fams


# ---------- H-07 compaction skip ----------

def test_h07_compaction_skip_detected(ws):
    _write_manifest(ws, [
        _item("ReleaseQueue", "compact", "function compact(address v) internal { for (uint i=0;i<r.amounts.length;){ paid+=r.amounts[i]; unchecked{++i;} } }", "function:ReleaseQueue:compact#01"),
    ])
    _run()
    fams = {h["family"] for h in _report(ws)["detected"]}
    assert "queue_key_length_bound_divergence" in fams


def test_high_risk_ids_exposed(ws):
    _write_manifest(ws, [
        _item("Postbox", "commitMessage", "function commitMessage(Env e){ s.postbox[toHash(e)] = e.data; }", "function:Postbox:commitMessage#01"),
        _item("Postbox", "consumeMessage", "function consumeMessage(Env e){ return s.postbox[toTracingId(e)]; }", "function:Postbox:consumeMessage#02"),
    ])
    _run()
    assert _report(ws)["high_risk_manifest_ids"]            # non-empty → feeds advisory escalation
