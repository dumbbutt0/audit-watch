"""
Tests for the fee_wrapper_bypass RESEARCH lens (P307, conservative/low-precision). No LLM, no network.

Class: a fee layer wraps an underlying cross-chain action, but the action is public/unguarded so users bypass the
fee by calling it directly. From the P306 decent M-02 miss.

Covers: public unguarded action + fee layer fires low; access-modifier'd action silent; fee-charging entrypoint
silent; no fee layer in scope silent; non-action fn silent; view silent; research-only flags; decent anchor recovery.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_context  # noqa: E402
fwb = importlib.import_module("fee_wrapper_bypass_taxonomy")
audit = importlib.import_module("fee_wrapper_bypass_audit")


def _c(name, body, sig="", contract="DecentEthRouter", vis="public", fee=True):
    return fwb.classify(name, sig, "f.sol", contract, snippet=body, has_fee_layer=fee, visibility=vis)


_SEND = "{ dcntEth.sendAndCall{value: g}(a, d, b, amt, p, gas, cp); }"


# 1. public unguarded cross-chain action + fee layer -> low
def test_public_action_fires():
    out = _c("bridgeWithPayload", _SEND, sig="function bridgeWithPayload(uint16 d, uint a) public payable")
    assert out and out[0]["confidence"] == "low" and out[0]["finding_shape"] == "fee_wrapper_bypass"


# 2. action with an access modifier -> silent
def test_access_modifier_silent():
    assert _c("bridge", _SEND, sig="function bridge(uint16 d) public onlyUtb") == []


# 3. the fee-charging entrypoint itself -> silent
def test_fee_invoker_silent():
    out = _c("bridgeAndExecute", _SEND, sig="function bridgeAndExecute(...) public payable retrieveAndCollectFees(fees, info, sig)")
    assert out == []


# 4. no fee layer in scope -> silent
def test_no_fee_layer_silent():
    assert _c("bridgeWithPayload", _SEND, sig="function bridgeWithPayload() public payable", fee=False) == []


# 5. non-action function name -> silent
def test_non_action_silent():
    assert _c("setRouter", _SEND, sig="function setRouter(address r) public") == []


# 6. view -> silent
def test_view_silent():
    assert _c("estimateBridge", _SEND, sig="function estimateBridge() public view returns (uint)") == []


# 7. action name but no actual send primitive -> silent
def test_no_send_silent():
    assert _c("bridge", "{ destinationBridges[id] = addr; }", sig="function bridge(uint16 d) public") == []


# 8. research-only flags via the runner
def test_research_only_flags(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": "function:C:f#x", "kind": "function", "contract": "C", "name": "f", "file": "none.sol",
         "signature": "", "source_span": {"start_line": 1, "end_line": 1}, "in_scope": True}]}))
    old = sys.argv
    sys.argv = ["fee_wrapper_bypass_audit", "--quiet", "--no-source"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((tmp_path / "output" / "fee_wrapper_bypass_audit.json").read_text())
    assert r["is_gate"] is False and r["research_only"] is False and r["promotion"] == "advisory_only" and r["routes_in_production"] is False
    assert r["routed_manifest_ids"] == []


# 9. read-only decent anchor recovery: DecentEthRouter.bridge/bridgeWithPayload fire, controlled volume
def test_decent_anchor_recovery(monkeypatch):
    dc = ROOT / "audits" / "decent-2024-01-holdout"
    if not (dc / "output" / "coverage_manifest.json").exists():
        pytest.skip("decent manifest not present")
    # The M-02 anchor (DecentEthRouter.bridge/bridgeWithPayload) lives in the decent-bridge lib submodule. The
    # detector recovers it from the function BODY, so the recovery test needs that source in the checkout. When the
    # lib is absent (manifest still references it, but the .sol is not vendored here) skip rather than fail.
    anchor_src = dc / "contracts" / "lib" / "decent-bridge" / "src" / "DecentEthRouter.sol"
    if not anchor_src.exists():
        pytest.skip("decent-bridge lib source (DecentEthRouter.sol) not in this checkout — anchor body "
                    "unavailable, so the detector cannot recover bridge/bridgeWithPayload")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: dc)
    audit._FILE_CACHE.clear()
    old = sys.argv
    sys.argv = ["fee_wrapper_bypass_audit", "--manifest", str(dc / "output" / "coverage_manifest.json"), "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((dc / "output" / "fee_wrapper_bypass_audit.json").read_text())
    assert r["has_fee_layer"] is True
    fns = {c["function"] for c in r["candidates"]}
    assert "bridgeWithPayload" in fns or "bridge" in fns   # the anchor (M-02)
    assert r["raw_candidates"] <= 5, f"volume not controlled: {r['raw_candidates']}"
    assert r["routes_in_production"] is False and r["routed_manifest_ids"] == []
