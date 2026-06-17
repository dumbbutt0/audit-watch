"""
Tests for the transferable_position_cap_bypass RESEARCH lens (vultisig M-03 miss). No LLM, no network.

Class: a per-user cap (maxCapPerUser) keyed on ownership of a TRANSFERABLE position NFT (ERC721). Transferring the
NFT resets the cap (balanceOf -> 0), so the user re-buys and bypasses the per-user invariant.

Covers: cap+identity+erc721 fires; soulbound suppressed; non-erc721 suppressed; no cap silent; no identity silent;
view silent; research-only flags; vultisig anchor recovery; size-credit FP control = 0.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_context  # noqa: E402
tcb = importlib.import_module("transferable_position_cap_bypass_taxonomy")
audit = importlib.import_module("transferable_position_cap_bypass_audit")


def _c(name, body, sig="", contract="ILOPool", kind="function", is_erc721=True, soulbound=False):
    return tcb.classify(name, sig, "f.sol", contract, snippet=body, kind=kind, is_erc721=is_erc721, soulbound=soulbound)


_BUY = "{ if (balanceOf(recipient) == 0) { _mint(recipient, tokenId); } else { tokenId = tokenOfOwnerByIndex(recipient, 0); } require(raiseAmount <= saleInfo.maxCapPerUser - _position.raiseAmount, 'UC'); }"


# 1. cap + NFT identity + erc721 transferable -> high
def test_cap_bypass_fires():
    out = _c("buy", _BUY, sig="function buy(uint256 raiseAmount, address recipient) external")
    assert out and out[0]["confidence"] == "high" and out[0]["finding_shape"] == "transferable_position_cap_bypass"


# 2. soulbound (transfers blocked) -> silent
def test_soulbound_silent():
    assert _c("buy", _BUY, sig="function buy() external", soulbound=True) == []


# 3. non-ERC721 -> silent
def test_non_erc721_silent():
    assert _c("buy", _BUY, sig="function buy() external", is_erc721=False) == []


# 4. no per-user cap -> silent
def test_no_cap_silent():
    body = "{ if (balanceOf(recipient) == 0) { _mint(recipient, tokenId); } }"
    assert _c("buy", body, sig="function buy() external") == []


# 5. cap but no NFT identity marker -> silent
def test_no_identity_silent():
    body = "{ require(amount <= maxCapPerUser - contributed[msg.sender], 'UC'); contributed[msg.sender] += amount; }"
    assert _c("buy", body, sig="function buy() external") == []


# 6. view -> silent
def test_view_silent():
    assert _c("preview", _BUY, sig="function preview() external view returns (uint256)") == []


# 7. research-only flags via the runner
def test_research_only_flags(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": "function:C:f#x", "kind": "function", "contract": "C", "name": "f", "file": "none.sol",
         "signature": "", "source_span": {"start_line": 1, "end_line": 1}, "in_scope": True}]}))
    old = sys.argv
    sys.argv = ["transferable_position_cap_bypass_audit", "--manifest", str(tmp_path / "output" / "coverage_manifest.json"), "--quiet", "--no-source"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((tmp_path / "output" / "transferable_position_cap_bypass_audit.json").read_text())
    assert r["is_gate"] is False and r["research_only"] is True and r["routes_in_production"] is False
    assert r["routed_manifest_ids"] == []


# 8. read-only vultisig anchor recovery: ILOPool.buy fires, volume controlled
def test_vultisig_anchor_recovery(monkeypatch):
    vt = ROOT / "audits" / "vultisig-2024-06-holdout"
    if not (vt / "output" / "coverage_manifest.json").exists():
        pytest.skip("vultisig manifest not present")
    audit._FILE_CACHE.clear()
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: vt)
    old = sys.argv
    sys.argv = ["transferable_position_cap_bypass_audit", "--manifest", str(vt / "output" / "coverage_manifest.json"), "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((vt / "output" / "transferable_position_cap_bypass_audit.json").read_text())
    fns = {c["function"] for c in r["candidates"]}
    assert "buy" in fns
    assert r["raw_candidates"] <= 3, f"volume not controlled: {r['raw_candidates']}"
    assert r["routes_in_production"] is False and r["routed_manifest_ids"] == []


# 9. FP control: size-credit -> 0 candidates
def test_size_credit_fp_control(monkeypatch):
    sc = ROOT / "audits" / "size-credit-2024-06-blind"
    if not (sc / "output" / "coverage_manifest.json").exists():
        pytest.skip("size-credit manifest not present")
    audit._FILE_CACHE.clear()
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: sc)
    old = sys.argv
    sys.argv = ["transferable_position_cap_bypass_audit", "--manifest", str(sc / "output" / "coverage_manifest.json"), "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((sc / "output" / "transferable_position_cap_bypass_audit.json").read_text())
    assert r["raw_candidates"] == 0, f"FP on size-credit: {[(c['contract'],c['function']) for c in r['candidates']]}"
