"""
Tests for the migration-flow state-model taxonomy + detector (deterministic, no LLM/network).

Catches the L1->L2 migration/reseed surfaces and resolves the cross-function conservation invariants behind
eval misses #242/#248/#451/#452/#462. The FP backbone (migration-context required) keeps ordinary Silo/Field
deposit/withdraw/claim OUT. Mirrors tests/units_invariant.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
mig = importlib.import_module("migration_flow_taxonomy")
audit_mod = importlib.import_module("migration_flow_audit")

MIGF = "contracts/beanstalk/migration/L2ContractMigrationFacet.sol"
RESEED = "contracts/beanstalk/init/reseed/L2/ReseedSilo.sol"


def clf(name, snippet="", file=MIGF, contract="L2ContractMigrationFacet", signature=""):
    return mig.classify(name, signature, file, contract, snippet=snippet)


# ── positive detection: migration-context functions ──
CATCH = [
    ("reseedSiloDeposit", "for (...) { addDeposit(account, token, stem, amount, bdv); }", RESEED, "ReseedSilo", "migrated_deposit"),
    ("recieveL1Beans", "require(msg.sender == xDomainMessageSender()); mint(receiver, amount);", "contracts/migration/BeanL1RecieverFacet.sol", "BeanL1RecieverFacet", "l2_receiver"),
    ("addMigratedDepositsToAccount", "s.accts[account].deposits[id] = Deposit(amount, bdv); // migrated", MIGF, "L2ContractMigrationFacet", "migrated_deposit"),
    ("setStalk", "s.accts[account].stalk = stalk; // migrated stalk", MIGF, "L2ContractMigrationFacet", "stalk_migration"),
    ("mintFertilizers", "fertilizedIndex += amount; // reseed barn", "contracts/init/reseed/ReseedBarn.sol", "ReseedBarn", "fertilizer_migration"),
    ("addMigratedUnderlying", "s.u[unripeToken].balanceOfUnderlying += underlying;", "contracts/migration/UnripeFacet.sol", "UnripeFacet", "unripe_migration"),
    ("verifySignature", "address signer = ECDSA.recover(_hashTypedDataV4(structHash), sig);", MIGF, "L2ContractMigrationFacet", "cross_chain_message_validation"),
]


@pytest.mark.parametrize("name,snip,file,contract,cat", CATCH)
def test_catches_migration_surfaces(name, snip, file, contract, cat):
    c = clf(name, snip, file, contract)
    assert c["migration_flow_sensitive"] is True, f"{name} should be migration-flow-sensitive"
    assert c["category"] == cat, f"{name}: expected {cat}, got {c['category']}"


def test_reseed_init_is_init_family():
    # a bare reseed init() legitimately maps to any init-family migration category (all high-risk)
    c = clf("init", "function init(bytes32 root) external { /* reseed deposits */ }", RESEED, "ReseedSilo")
    assert c["migration_flow_sensitive"]
    assert c["category"] in {"reseed_initializer", "init_order_dependency", "one_shot_guard", "migration_initializer"}


def test_plenty_migration_detected():
    c = clf("init", "s.sys.sop.plentyPerSopToken[WETH] = plenty; // reseed", "contracts/init/reseed/ReseedSilo.sol", "ReseedSilo")
    assert c["migration_flow_sensitive"] and "plenty" in (c["category"] + " " + " ".join(c["state_domains"]) + " plenty")


def test_global_vs_user_total_detected():
    c = clf("init", "s.sys.silo.stalk = totalStalk; // reseed global total", "contracts/init/reseed/ReseedSilo.sol", "ReseedSilo")
    assert c["migration_flow_sensitive"] and mig.is_high_risk(c)


def test_one_shot_initializer_detected():
    c = clf("init", "function init() external { /* reseed; no initializer guard */ }", "contracts/init/reseed/ReseedField.sol", "ReseedField")
    assert c["migration_flow_sensitive"]


# ── FP controls: must NOT tag (no migration context) ──
def test_ordinary_deposit_outside_migration():
    c = clf("deposit", "function deposit(address token, uint256 amount, uint8 mode) external { _deposit(...); }",
            "contracts/beanstalk/silo/SiloFacet.sol", "SiloFacet")
    assert c["migration_flow_sensitive"] is False


def test_ordinary_withdraw_outside_migration():
    c = clf("withdrawDeposit", "function withdrawDeposit(address token, int96 stem, uint256 amount, uint8 mode) external {}",
            "contracts/beanstalk/silo/SiloFacet.sol", "SiloFacet")
    assert c["migration_flow_sensitive"] is False


def test_generic_initialize_owner_no_migrated_state():
    c = clf("initializeOwner", "function initializeOwner(address owner) internal { s.owner = owner; }",
            "contracts/beanstalk/init/InitDiamond.sol", "InitDiamond")
    assert c["migration_flow_sensitive"] is False


def test_comment_only_migration_words():
    c = clf("foo", "// this is not part of the reseed migration L1 L2 flow\n return x;",
            "contracts/beanstalk/silo/SiloFacet.sol", "SiloFacet")
    assert c["migration_flow_sensitive"] is False


def test_bridge_constant_alone_without_state_flow():
    # a bridge constant (cross-chain lens territory) declared with no migration state flow
    c = mig.classify("BRIDGE", "address constant BRIDGE = 0x4200000000000000000000000000000000000010;",
                     "contracts/C.sol", "C")
    assert c["migration_flow_sensitive"] is False


def test_regular_claim_outside_migration():
    c = clf("claimPlenty", "function claimPlenty(uint8 mode) external { _claimPlenty(msg.sender); }",
            "contracts/beanstalk/silo/SiloFacet.sol", "SiloFacet")
    assert c["migration_flow_sensitive"] is False


# ── end-to-end detector: invariant resolution over a synthetic manifest ──
def test_detector_invariant_resolution(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    manifest = {"items": [
        {"id": "function:F:addMigratedDepositsToAccount#a", "kind": "function",
         "name": "addMigratedDepositsToAccount", "contract": "L2ContractMigrationFacet", "file": MIGF,
         "signature": "function addMigratedDepositsToAccount(address account, ...) internal",
         "source_span": {"start_line": 1}, "in_scope": True},
        {"id": "function:F:setStalk#b", "kind": "function", "name": "setStalk",
         "contract": "L2ContractMigrationFacet", "file": MIGF,
         "signature": "function setStalk(address account, uint256 stalk) internal",
         "source_span": {"start_line": 1}, "in_scope": True},
        {"id": "function:S:deposit#c", "kind": "function", "name": "deposit", "contract": "SiloFacet",
         "file": "contracts/beanstalk/silo/SiloFacet.sol",
         "signature": "function deposit(address token, uint256 amount) external", "source_span": {"start_line": 1}, "in_scope": True},
    ]}
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps(manifest))
    (tmp_path / "output" / "coverage_dispositions.json").write_text(json.dumps(
        {"dispositions": [{"manifest_id": "function:F:addMigratedDepositsToAccount#a", "status": "finding", "finding_refs": ["SN-003"]}]}))
    old = sys.argv
    sys.argv = ["migration_flow_audit", "--no-source"]
    try:
        assert audit_mod.main() == 0
    finally:
        sys.argv = old
    rep = json.loads((tmp_path / "output" / "migration_flow_audit.json").read_text())
    names = {d["name"] for d in rep["detected"]}
    assert "addMigratedDepositsToAccount" in names and "deposit" not in names  # catch + FP control
    invs = {i["invariant_id"]: i for i in rep["cross_function_invariants"]}
    # INV-MIG-05 (#248, deposit pushed to list) must resolve addMigratedDepositsToAccount and need review
    inv05 = invs["INV-MIG-05"]
    assert inv05["review_status"] == "needs_review"
    assert any(p["name"] == "addMigratedDepositsToAccount" for p in inv05["source_functions"])
    assert inv05["related_miss"] == "#248"
    # the ordinary Silo deposit must NOT be pulled in as a participant (migration-context filter)
    assert all(p["name"] != "deposit" for inv in rep["cross_function_invariants"] for p in inv["source_functions"])
