"""
Tests for the create_time_reentrancy RESEARCH family. No LLM/network. Synthetic ADVANCE/REJECT cases + negative
controls + a mechanism-based replay over the real nextgen NextGenCore.mint anchor (H-01: _safeMint before counter).
"""
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

ctr = importlib.import_module("create_time_reentrancy_taxonomy")
audit = importlib.import_module("create_time_reentrancy_audit")


def _c(name, body, mods=None, contract="C", sig=""):
    return ctr.classify(contract, name, sig, body, modifiers=mods or [])


# 1. mint: _safeMint (callback) BEFORE counter commit, no guard -> ADVANCE high
def test_1_safemint_before_commit_advances():
    body = "function mint(address to) external { _safeMint(to, id); tokensMintedPerAddress[to] += 1; }"
    out = _c("mint", body)
    assert out and out[0]["confidence"] == "high", out
    assert out[0]["finding_shape"] == "create_time_reentrancy"


# 2. mint: counter commit BEFORE _safeMint (CEI-correct) -> REJECT
def test_2_commit_before_callback_rejected():
    body = "function mint(address to) external { tokensMintedPerAddress[to] += 1; _safeMint(to, id); }"
    assert _c("mint", body) == []


# 3. mint with nonReentrant guard -> REJECT
def test_3_guarded_rejected():
    body = "function mint(address to) external nonReentrant { _safeMint(to, id); minted[to] += 1; }"
    assert _c("mint", body, mods=["nonReentrant"]) == []


# 4. non-create function (transfer) -> REJECT (S1 fails)
def test_4_non_create_verb_rejected():
    body = "function withdrawTo(address to) external { _safeTransfer(token, to, 1); balances[to] += 1; }"
    assert _c("withdrawTo", body) == []


# 5. create fn with callback but NO post-callback state commit -> REJECT (S3 fails)
def test_5_no_post_commit_rejected():
    body = "function createListing(address to) external { safeTransferFrom(seller, to, id); emit Listed(to); }"
    assert _c("createListing", body) == []


# 6. negative control: view getter -> REJECT
def test_6_view_getter_rejected():
    body = "function getMintCount(address u) external view returns (uint256) { return minted[u]; }"
    assert _c("getMintCount", body) == []


# 7. (P242 precision fix) ERC20 deposit: SafeERC20.safeTransferFrom BEFORE _mint is the INTENTIONAL CEI-safe deposit
#    pattern (pooltogether/sentiment/concrete/reserve FPs) -> REJECT (ERC20 safeTransferFrom dropped from callback set;
#    ERC20 transferFrom triggers no recipient callback).
def test_7_erc20_deposit_before_mint_rejected():
    body = "function deposit(uint256 a, address r) external { _asset.safeTransferFrom(msg.sender, address(this), a); _mint(r, a); }"
    assert _c("deposit", body) == []


# ---- mechanism-based replay: real nextgen NextGenCore.mint anchor (H-01) ----
def test_nextgen_anchor_recovered(tmp_path):
    core = ROOT / "audits/nextgen-2023-10-fresh/_src/smart-contracts/NextGenCore.sol"
    if not core.exists():
        import pytest
        pytest.skip("nextgen NextGenCore.sol not present")
    rel = str(core.relative_to(ROOT))
    manifest = {"items": [
        {"id": "function:NextGenCore:mint", "kind": "function", "contract": "NextGenCore", "name": "mint",
         "file": rel, "source_span": {"start_line": 189}, "in_scope": True, "modifiers": []},
        {"id": "function:NextGenCore:_mintProcessing", "kind": "function", "contract": "NextGenCore",
         "name": "_mintProcessing", "file": rel, "source_span": {"start_line": 227}, "in_scope": True, "modifiers": []},
    ]}
    man = tmp_path / "coverage_manifest.json"
    man.write_text(json.dumps(manifest))
    out = tmp_path / "ctr_audit.json"
    audit._FILE_CACHE.clear()
    sys.argv = ["create_time_reentrancy_audit.py", "--manifest", str(man), "--out", str(out), "--quiet"]
    assert audit.main() == 0
    rep = json.loads(out.read_text())
    assert rep["routed_manifest_ids"] == [] and rep["research_only"] is True
    hit = [c for c in rep["candidates"] if c["contract"] == "NextGenCore" and c["function"] == "mint"]
    assert hit and hit[0]["confidence"] == "high", [c["function"] for c in rep["candidates"]]
