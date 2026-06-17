"""
Tests for the crosschain_refund_recipient RESEARCH lens (P307). No LLM, no network.

Class: cross-chain value flows refund to the wrong recipient. From P306 decent M-05 (refund=msg.sender in an
intermediary) + H-03 (executor failure-refund to a source-chain `from`).

Covers: (i) intermediary send refund=msg.sender fires; non-intermediary direct entrypoint silent; (ii) executor
failure-refund to `from` fires; refund to address(this) silent; no failure branch silent; view silent;
research-only flags; decent anchor recovery (both sub-shapes).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_context  # noqa: E402
crr = importlib.import_module("crosschain_refund_recipient_taxonomy")
audit = importlib.import_module("crosschain_refund_recipient_audit")


def _c(name, body, sig="", contract="DecentEthRouter", kind="function"):
    return crr.classify(name, sig, "f.sol", contract, snippet=body, kind=kind)


# 1. (i) intermediary cross-chain send, refundAddress = payable(msg.sender) -> fires
def test_refund_to_msg_sender_fires():
    body = "{ LzCallParams memory cp = LzCallParams({refundAddress: payable(msg.sender), zro: address(0), ap: ap}); dcntEth.sendAndCall{value: g}(a, d, b, amt, p, gas, cp); }"
    out = _c("_bridgeWithPayload", body, contract="DecentEthRouter")
    assert any(c["finding_shape"] == "crosschain_refund_to_msg_sender" for c in out)


# 2. (i) non-intermediary contract with a direct user send -> silent (no asymmetry/intermediary)
def test_non_intermediary_silent():
    body = "{ endpoint.sendAndCall{value: g}(a, d, b, amt, p, gas, LzCallParams({refundAddress: payable(msg.sender)})); }"
    assert _c("bridgeMyEth", body, contract="MyWallet") == []


# 3. (ii) executor failure-refund to `from` -> fires
def test_failure_refund_to_from_fires():
    sig = "function _executeWeth(address from, address target, uint256 amount, bytes memory callPayload) private"
    body = "{ weth.approve(target, amount); (bool success, ) = target.call(callPayload); if (!success) { weth.transfer(from, amount); return; } }"
    out = _c("_executeWeth", body, sig=sig, contract="DecentBridgeExecutor")
    assert any(c["finding_shape"] == "crosschain_refund_to_source_param" for c in out)


# 4. (ii) refund to address(this) (not the source param) -> silent
def test_self_refund_silent():
    sig = "function exec(address from, address target, uint256 amount) external"
    body = "{ (bool success, ) = target.call(''); if (!success) { token.transfer(address(this), amount); } }"
    assert _c("exec", body, sig=sig, contract="Executor") == []


# 5. (ii) no failure branch -> silent
def test_no_failure_branch_silent():
    sig = "function exec(address from, address target, uint256 amount) external"
    body = "{ (bool success, ) = target.call(''); token.transfer(from, amount); }"
    assert all(c["finding_shape"] != "crosschain_refund_to_source_param" for c in _c("exec", body, sig=sig, contract="Executor"))


# 6. view -> silent
def test_view_silent():
    body = "{ return dcntEth.estimateSendAndCallFee(d, b, amt, p, gas, false, ap); }"
    assert _c("estimateFee", body, sig="function estimateFee() public view returns (uint)", contract="DecentEthRouter") == []


# 7. research-only flags via the runner
def test_research_only_flags(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": "function:C:f#x", "kind": "function", "contract": "C", "name": "f", "file": "none.sol",
         "signature": "", "source_span": {"start_line": 1, "end_line": 1}, "in_scope": True}]}))
    old = sys.argv
    sys.argv = ["crosschain_refund_recipient_audit", "--quiet", "--no-source"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((tmp_path / "output" / "crosschain_refund_recipient_audit.json").read_text())
    assert r["is_gate"] is False and r["research_only"] is False and r["promotion"] == "advisory_only" and r["routes_in_production"] is False
    assert r["routed_manifest_ids"] == []


# 8. read-only decent anchor recovery: both sub-shapes fire on the real loci, controlled volume
def test_decent_anchor_recovery(monkeypatch):
    dc = ROOT / "audits" / "decent-2024-01-holdout"
    if not (dc / "output" / "coverage_manifest.json").exists():
        pytest.skip("decent manifest not present")
    # The anchor (DecentEthRouter._bridgeWithPayload) is in the decent-bridge lib submodule; the detector recovers
    # it from the function BODY, so skip when that source isn't vendored in this checkout (manifest still refs it).
    if not (dc / "contracts" / "lib" / "decent-bridge" / "src" / "DecentEthRouter.sol").exists():
        pytest.skip("decent-bridge lib source (DecentEthRouter.sol) not in this checkout — anchor body unavailable")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: dc)
    audit._FILE_CACHE.clear()
    old = sys.argv
    sys.argv = ["crosschain_refund_recipient_audit", "--manifest", str(dc / "output" / "coverage_manifest.json"), "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((dc / "output" / "crosschain_refund_recipient_audit.json").read_text())
    pairs = {(c["contract"], c["function"], c["finding_shape"]) for c in r["candidates"]}
    assert ("DecentEthRouter", "_bridgeWithPayload", "crosschain_refund_to_msg_sender") in pairs   # M-05
    assert any(fn in ("_executeWeth", "_executeEth") and shp == "crosschain_refund_to_source_param"
               for (_, fn, shp) in pairs)                                                          # H-03
    assert r["raw_candidates"] <= 8, f"volume not controlled: {r['raw_candidates']}"
    assert r["routes_in_production"] is False and r["routed_manifest_ids"] == []
