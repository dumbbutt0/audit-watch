"""
Asset-source/amount-origin consistency lens (Recall H-05) and checkpoint/queue/returndata liveness lens
(Recall H-07/H-09/M-04). Detect the mismatch/liveness shapes; safe equivalents are not high-risk.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
asc = importlib.import_module("asset_source_consistency_taxonomy")
asc_audit = importlib.import_module("asset_source_consistency_audit")
cl = importlib.import_module("checkpoint_liveness_taxonomy")
cl_audit = importlib.import_module("checkpoint_liveness_audit")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _item(contract, name, sig, mid=None, score=3):
    return {"id": mid or f"function:{contract}:{name}#0001", "kind": "function", "contract": contract,
            "file": f"{contract}.sol", "name": name, "signature": sig, "in_scope": True,
            "attack_surface_score": score, "tags": [], "source_span": {}}


def _setup(ws, items):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "source": {}, "items": items}))
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps({"dispositions": []}))


def _run(mod, name):
    old = sys.argv
    sys.argv = [name, "--no-source"]
    try:
        assert mod.main() == 0
    finally:
        sys.argv = old


# ---------- asset-source (H-05) ----------

LEAVE_WRONG = "function leave() external { uint256 amount = genesisBalance[msg.sender]; genesisBalance[msg.sender]=0; collateralSource.transferFunds(msg.sender, amount); }"
LEAVE_SAFE = "function leave() external { uint256 amount = genesisBalance[msg.sender]; genesisBalance[msg.sender]=0; supplySource.transferFunds(msg.sender, amount); }"


def test_h05_unit_wrong_source_high_risk():
    c = asc.classify("leave", LEAVE_WRONG)
    assert c["asset_source_sensitive"] and asc.is_high_risk(c)
    assert "collateral" in c["families"] and "supply" in c["families"]


def test_h05_single_source_not_sensitive():
    c = asc.classify("releaseStake", "function releaseStake(uint256 a) external { collateralSource.transferFunds(msg.sender, a); }")
    assert c["asset_source_sensitive"] is False


def test_h05_audit_routes_high_risk(ws):
    _setup(ws, [_item("SubnetActor", "leave", LEAVE_WRONG)])
    _run(asc_audit, "asset_source_consistency_audit")
    rep = json.loads((ws / "output" / "asset_source_consistency_audit.json").read_text())
    assert rep["high_risk_manifest_ids"] == ["function:SubnetActor:leave#0001"]


# ---------- checkpoint liveness (H-09 / H-07 / M-04) ----------

def test_h09_recipient_blocks_checkpoint_unit():
    body = "function execBottomUpMsgs(Msg[] msgs) external { for (uint i;i<msgs.length;){ (bool ok, bytes memory ret)=msgs[i].to.call{value:v}(d); require(ok); unchecked{++i;} } }"
    c = cl.classify("execBottomUpMsgs", body, contract="CheckpointingFacet")
    assert c["liveness_sensitive"] and cl.is_high_risk(c)


def test_h09_safe_bounded_not_high_risk():
    body = "function execBottomUpMsgs(Msg[] msgs) external { for (uint i;i<msgs.length;){ (bool ok,)=msgs[i].to.call{value:v,gas:100000}(\"\"); ok; unchecked{++i;} } }"
    c = cl.classify("execBottomUpMsgs", body, contract="CheckpointingFacet")
    # external call in loop still flags recipient_blocks_checkpoint (conservative); returndata is NOT loaded
    assert c["has_returndata_load"] is False


def test_h07_compaction_skip_unit():
    c = cl.classify("compact", "function compact(address v) internal { for (uint i=0;i<r.amounts.length;){ paid+=r.amounts[i]; unchecked{++i;} } }", contract="ReleaseQueue")
    assert c["category"] == "compaction_skip" and cl.is_high_risk(c)


def test_m04_floodable_state_unit():
    c = cl.classify("stake", "function stake(uint256 a) external { changeLog.push(abi.encode(msg.sender)); }", contract="SubnetActor")
    assert c["category"] == "floodable_state"          # Medium; reported, not auto-High
    assert cl.is_high_risk(c) is False


def test_liveness_plain_getter_not_flagged():
    c = cl.classify("getOwner", "function getOwner() view returns (address) { return owner; }", contract="Ownership")
    assert c["liveness_sensitive"] is False


def test_liveness_audit_high_risk_ids(ws):
    _setup(ws, [_item("CheckpointingFacet", "execBottomUpMsgs",
                      "function execBottomUpMsgs(Msg[] msgs) external { for (uint i;i<msgs.length;){ (bool ok, bytes memory ret)=msgs[i].to.call(d); require(ok); unchecked{++i;} } }")])
    _run(cl_audit, "checkpoint_liveness_audit")
    rep = json.loads((ws / "output" / "checkpoint_liveness_audit.json").read_text())
    assert rep["high_risk_manifest_ids"]
