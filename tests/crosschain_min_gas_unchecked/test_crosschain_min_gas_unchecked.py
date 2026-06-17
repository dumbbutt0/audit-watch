"""
Tests for the crosschain_min_gas_unchecked RESEARCH lens (P307). No LLM, no network.

Class: a cross-chain send forwards a caller-supplied destination-gas amount with no minimum floor -> dst execution
reverts. From the P306 decent H-02 miss.

Covers: send + unfloored dstGas fires; explicit min-gas check silent; view fee-estimator silent; no send silent;
no gas param silent; library silent; research-only flags; decent anchor recovery (DecentEthRouter bridge* fire).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_context  # noqa: E402
cmg = importlib.import_module("crosschain_min_gas_unchecked_taxonomy")
audit = importlib.import_module("crosschain_min_gas_unchecked_audit")


def _c(name, body, sig="", contract="Router", kind="function"):
    return cmg.classify(name, sig, "f.sol", contract, snippet=body, kind=kind)


_ANCHOR_BODY = "{ dcntEth.sendAndCall{value: gasValue}(address(this), _dstChainId, destBridge, _amount, payload, _dstGasForCall, callParams); }"
_ANCHOR_SIG = "function bridgeWithPayload(uint16 _dstChainId, address _toAddress, uint _amount, bool deliverEth, uint64 _dstGasForCall, bytes memory additionalPayload) public payable"


# 1. send + unfloored dstGasForCall -> high
def test_anchor_high():
    out = _c("bridgeWithPayload", _ANCHOR_BODY, sig=_ANCHOR_SIG)
    assert out and out[0]["confidence"] == "high"
    assert out[0]["finding_shape"] == "crosschain_min_gas_unchecked"


# 2. explicit min-gas check -> silent
def test_min_check_silent():
    body = "{ require(_dstGasForCall >= MIN_GAS, 'gas'); dcntEth.sendAndCall(a, b, c, amt, p, _dstGasForCall, cp); }"
    assert _c("bridgeWithPayload", body, sig=_ANCHOR_SIG) == []


# 3. min-gas constant marker -> silent
def test_min_gas_marker_silent():
    body = "{ uint64 g = _dstGasForCall < minGas ? minGas : _dstGasForCall; dcntEth.sendAndCall(a,b,c,amt,p,g,cp); }"
    assert _c("bridgeWithPayload", body, sig=_ANCHOR_SIG) == []


# 4. view fee-estimator -> silent
def test_view_estimator_silent():
    sig = "function estimateSendAndCallFee(uint16 d, uint a, uint64 _dstGasForCall) public view returns (uint)"
    body = "{ return dcntEth.estimateSendAndCallFee(d, dst, a, p, _dstGasForCall, false, ap); }"
    assert _c("estimateSendAndCallFee", body, sig=sig) == []


# 5. no cross-chain send -> silent
def test_no_send_silent():
    assert _c("setGas", "{ dstGas = _dstGasForCall; }", sig="function setGas(uint64 _dstGasForCall) external") == []


# 6. send but no dst-gas param -> silent
def test_no_gas_silent():
    assert _c("bridge", "{ dcntEth.sendAndCall(a, b, c, amt, p, callParams); }", sig="function bridge() public payable") == []


# 7. library -> silent
def test_library_silent():
    assert _c("lzSend", "{ lzSend(d, payload, refund, zro, _dstGasForCall); }", sig="function lzSend(uint64 _dstGasForCall) internal", contract="LzApp", kind="library") == []


# 8. research-only flags via the runner
def test_research_only_flags(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": "function:C:f#x", "kind": "function", "contract": "C", "name": "f", "file": "none.sol",
         "signature": "", "source_span": {"start_line": 1, "end_line": 1}, "in_scope": True}]}))
    old = sys.argv
    sys.argv = ["crosschain_min_gas_unchecked_audit", "--quiet", "--no-source"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((tmp_path / "output" / "crosschain_min_gas_unchecked_audit.json").read_text())
    assert r["is_gate"] is False and r["research_only"] is False and r["promotion"] == "advisory_only" and r["routes_in_production"] is False
    assert r["routed_manifest_ids"] == []


# 9. read-only decent anchor recovery: DecentEthRouter bridge functions fire, controlled volume
def test_decent_anchor_recovery(monkeypatch):
    dc = ROOT / "audits" / "decent-2024-01-holdout"
    if not (dc / "output" / "coverage_manifest.json").exists():
        pytest.skip("decent manifest not present")
    # The anchor (DecentEthRouter.bridgeWithPayload) is in the decent-bridge lib submodule; the detector recovers
    # it from the function BODY, so skip when that source isn't vendored in this checkout (manifest still refs it).
    if not (dc / "contracts" / "lib" / "decent-bridge" / "src" / "DecentEthRouter.sol").exists():
        pytest.skip("decent-bridge lib source (DecentEthRouter.sol) not in this checkout — anchor body unavailable")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: dc)
    audit._FILE_CACHE.clear()
    old = sys.argv
    sys.argv = ["crosschain_min_gas_unchecked_audit", "--manifest", str(dc / "output" / "coverage_manifest.json"), "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((dc / "output" / "crosschain_min_gas_unchecked_audit.json").read_text())
    fns = {c["function"] for c in r["candidates"]}
    assert "bridgeWithPayload" in fns   # the anchor (H-02)
    assert r["raw_candidates"] <= 5, f"volume not controlled: {r['raw_candidates']}"
    assert r["routes_in_production"] is False and r["routed_manifest_ids"] == []
