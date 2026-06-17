"""
Tests for the Field-DoS / griefing taxonomy + detector (deterministic, no LLM/network).

Models attacker-controlled COST ASYMMETRY behind eval misses #379 (plot-spam transfer DoS), #485 (plotIndexes
duplication), #491 (transferDeposit amount==0 recipient DoS). The griefing-PRIMITIVE GATE (push / growable
state var / zero-amount guard / recipient value-call) keeps the lens focused — NOT a flag-all-loops sweep.
Mirrors tests/migration_flow.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
grief = importlib.import_module("griefing_dos_taxonomy")
audit_mod = importlib.import_module("griefing_dos_audit")


def clf(name, snippet="", file="contracts/beanstalk/field/FieldFacet.sol", contract="FieldFacet", signature=""):
    return grief.classify(name, signature, file, contract, snippet=snippet)


# ── positive detection (each snippet carries a real griefing primitive) ──
def test_plot_transfer_user_indexes():
    c = clf("transferPlots", "for (uint i; i < ids.length; ++i) { plotIndexes[recipient].push(ids[i]); }",
            "contracts/beanstalk/market/MarketplaceFacet.sol", "MarketplaceFacet")
    assert c["griefing_sensitive"] and c["category"] == "plot_spam"


def test_pod_fragmentation():
    c = clf("_createPodListing", "podListings[account].push(id); // fragment",
            "contracts/beanstalk/market/Listing.sol", "Listing")
    assert c["griefing_sensitive"] and c["category"] in ("pod_fragmentation", "storage_growth", "array_bloat")


def test_caller_controlled_push():
    c = clf("addEntry", "depositIdList[account].push(id);", "contracts/beanstalk/silo/TokenSilo.sol", "TokenSilo")
    assert c["griefing_sensitive"]


def test_loop_over_storage_array_of_user_entries():
    c = clf("_transferPlots", "for (uint i; i < plotIndexes[sender].length; ++i) { ... }",
            "contracts/beanstalk/market/MarketplaceFacet.sol", "MarketplaceFacet")
    assert c["griefing_sensitive"] and grief.is_high_risk(c)


def test_zero_amount_entry_creation():
    c = clf("transferDeposit", "function transferDeposit(...) { /* no positive-amount guard */ depositIdList[to].push(id); }",
            "contracts/beanstalk/silo/SiloFacet.sol", "SiloFacet",
            signature="function transferDeposit(address sender, address recipient, address token, int96 stem, uint256 amount) external")
    assert c["griefing_sensitive"]


def test_recipient_value_revert_dos():
    c = clf("_settle", "(bool ok,) = recipient.call{value: amount}(''); require(ok);",
            "contracts/beanstalk/Settle.sol", "Settle")
    assert c["griefing_sensitive"] and c["category"] == "recipient_revert_dos"


def test_cleanup_missing():
    c = clf("removeDeposit", "depositIdList[account].pop(); delete deposits[id];",
            "contracts/beanstalk/silo/TokenSilo.sol", "TokenSilo")
    assert c["griefing_sensitive"]


# ── FP controls: must NOT tag (no griefing primitive) ──
def test_fixed_small_loop_not_tagged():
    c = clf("sumThree", "for (uint i; i < 3; ++i) { total += arr[i]; } return total;",
            "contracts/Lib.sol", "Lib")
    assert c["griefing_sensitive"] is False


def test_view_balance_getter_not_high_risk():
    # loops over a token list but read-only and no growable-state primitive
    c = clf("getAllBalances", "for (uint i; i < tokens.length; ++i) { b[i] = bal(tokens[i]); }",
            "contracts/beanstalk/silo/SiloGettersFacet.sol", "SiloGettersFacet",
            signature="function getAllBalances(address account) external view returns (uint256[] memory)")
    # either untagged (no primitive) or at least NOT high-risk
    assert grief.is_high_risk(c) is False


def test_admin_only_loop_over_config_not_tagged():
    c = clf("setWhitelist", "for (uint i; i < tokens.length; ++i) { ss[tokens[i]] = settings[i]; }",
            "contracts/beanstalk/init/Whitelist.sol", "Whitelist",
            signature="function setWhitelist(address[] tokens) external onlyOwner")
    assert c["griefing_sensitive"] is False


def test_pure_helper_loop_not_tagged():
    c = clf("max", "for (uint i; i < a.length; ++i) { if (a[i] > m) m = a[i]; } return m;",
            "contracts/LibMath.sol", "LibMath", signature="function max(uint256[] memory a) internal pure returns (uint256)")
    assert grief.is_high_risk(c) is False


def test_single_mapping_balance_update_not_tagged():
    c = clf("setBalance", "s.accts[account].balance = amount;", "contracts/beanstalk/Token.sol", "Token")
    assert c["griefing_sensitive"] is False


def test_token_receiver_callback_not_griefing():
    # onERC1155Received with no plot/deposit state -> token-standard lens territory, not griefing
    c = clf("onERC1155Received", "return this.onERC1155Received.selector;", "contracts/Recv.sol", "Recv")
    assert c["griefing_sensitive"] is False


def test_comment_only_spam_words_not_tagged():
    c = clf("foo", "// guard against plotIndexes spam / DoS griefing here\n return x;", "contracts/Lib.sol", "Lib")
    assert c["griefing_sensitive"] is False


# ── end-to-end: state-growth surface pairing (creator sow ↔ consumer transferPlots) ──
def test_detector_surface_pairing(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    MF = "contracts/beanstalk/market/MarketplaceFacet.sol"
    manifest = {"items": [
        {"id": "function:F:sow#a", "kind": "function", "name": "sow", "contract": "FieldFacet",
         "file": "contracts/beanstalk/field/FieldFacet.sol",
         "signature": "function sow(uint256 beans) external returns (uint256)",
         "source_span": {"start_line": 2, "end_line": 2}, "in_scope": True},
        {"id": "function:M:transferPlots#b", "kind": "function", "name": "transferPlots", "contract": "MarketplaceFacet",
         "file": MF, "signature": "function transferPlots(...) external", "source_span": {"start_line": 2, "end_line": 2}, "in_scope": True},
        {"id": "function:S:getBal#c", "kind": "function", "name": "getBal", "contract": "SiloGettersFacet",
         "file": "contracts/beanstalk/silo/SiloGettersFacet.sol",
         "signature": "function getBal(address a) external view returns (uint256)", "source_span": {"start_line": 2, "end_line": 2}, "in_scope": True},
    ]}
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps(manifest))
    (tmp_path / "output" / "coverage_dispositions.json").write_text(json.dumps(
        {"dispositions": [{"manifest_id": "function:M:transferPlots#b", "status": "cleared", "clear_reason": "standard plot transfer"}]}))
    # monkeypatch source so snippets carry the plotIndexes primitive
    src_field = ["library F {", "function sow(uint256 beans) external returns (uint256) { plotIndexes[msg.sender].push(id); }", "}"]
    src_mkt = ["library M {", "function transferPlots(...) external { for (uint i; i < plotIndexes[sender].length; ++i) {} }", "}"]
    src_silo = ["library S {", "function getBal(address a) external view returns (uint256) { return b[a]; }", "}"]
    (tmp_path / "f.sol").write_text("\n".join(src_field))
    monkeypatch.setattr(audit_mod, "ROOT", tmp_path)
    # write the real source files at the manifest paths under tmp ROOT
    for rel, lines in [("contracts/beanstalk/field/FieldFacet.sol", src_field),
                       (MF, src_mkt),
                       ("contracts/beanstalk/silo/SiloGettersFacet.sol", src_silo)]:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(lines))
    old = sys.argv
    sys.argv = ["griefing_dos_audit"]
    try:
        assert audit_mod.main() == 0
    finally:
        sys.argv = old
    rep = json.loads((tmp_path / "output" / "griefing_dos_audit.json").read_text())
    names = {d["name"] for d in rep["detected"]}
    assert "sow" in names and "transferPlots" in names and "getBal" not in names  # catch + view FP control
    plots = next((s for s in rep["state_growth_surfaces"] if s["surface"] == "plots"), None)
    assert plots and plots["asymmetric_pairing"] is True  # creator sow ↔ consumer transferPlots
    assert any(x["name"] == "transferPlots" for x in rep["previously_cleared_high_risk"])
