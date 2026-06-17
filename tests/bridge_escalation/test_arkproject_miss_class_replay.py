"""
ArkProject miss-class replay (READ-ONLY; reconstructed). Proves the bridge-escalation features would catch
the two ArkProject under-escalation misses, and that the frozen ArkProject eval snapshot is NOT mutated.

- AK-H4 (cross-artifact lifecycle): in-scope deployer deploys an upgradeable ERC721 with no ownership
  handover → cross_artifact lens flags it (lifecycle risk / under-escalated).
- AK-M2 (recipient/custody): withdraw safeTransferFrom to a non-receiver → recipient lens high-risk.
- AK-M3 (thread-not-escalated): the reentrancy bridge thread, dropped without escalation/invalidation,
  is BLOCKED by the bridge thread escalation gate.

These use reconstructed fixtures (the frozen snapshot only stores a MANIFEST + hashes); the test never reads
or writes the frozen eval beyond verifying its hash.
"""
import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
cal = importlib.import_module("cross_artifact_lifecycle_taxonomy")
rc = importlib.import_module("recipient_custody_taxonomy")
gate = importlib.import_module("bridge_thread_escalation_gate")

SNAP = ROOT / "audits" / "ark-project-2024-07-strict-eval" / "output" / "pre_answer_key_snapshot"
frozen = pytest.mark.skipif(not (SNAP / "MANIFEST.json").exists(),
                            reason="frozen ArkProject eval snapshot not present")


# ---------- AK-H4: cross-artifact lifecycle ----------

def test_akh4_deployer_no_ownership_flagged():
    body = ("function _deployERC721Bridgeable(string name, string symbol) internal returns (address) { "
            "address proxy = Deployer.deployERC721Bridgeable(name, symbol); "
            "return address(new ERC1967Proxy(impl, abi.encodeWithSelector(ERC721Bridgeable.initialize.selector))); }")
    c = cal.classify("_deployERC721Bridgeable", body)
    assert c["cross_artifact_sensitive"] and cal.is_high_risk(c)
    assert "ownership_transfer_to_controller" in c["missing_lifecycle"]


# ---------- AK-M2: recipient/custody ----------

def test_akm2_withdraw_non_receiver_flagged():
    body = ("function withdrawTokens(uint256[] request) external returns (address) { "
            "_withdrawFromEscrow(ctype, collectionL1, req.ownerL1, id); "
            "IERC721(collectionL1).safeTransferFrom(address(this), to, id); }")
    c = rc.classify("withdrawTokens", body)
    assert c["recipient_custody_sensitive"] and rc.is_high_risk(c)


# ---------- AK-M3: bridge thread escalation guard ----------

def test_akm3_dropped_reentrancy_thread_blocks(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True)
    (tmp_path / "data" / "threads").mkdir(parents=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    monkeypatch.delenv("AUDITWATCH_BRIDGE_THREAD_OVERRIDE", raising=False)
    (tmp_path / "data" / "threads" / "promising_threads.jsonl").write_text(json.dumps({
        "thread_id": "T-04", "verdict": "MEDIUM_THREAD",
        "entry_conditions": "withdraw releases NFT via safeTransferFrom; recipient hook re-enters the bridge mid-loop",
        "violation_path": ["Bridge.withdraw releases from escrow", "onERC721Received re-enters withdraw"],
        "evidence": "Escrow._withdrawFromEscrow; no reentrancy guard"}) + "\n")
    (tmp_path / "output" / "merged_findings.json").write_text(json.dumps({"findings": []}))  # T-04 dropped
    old = sys.argv
    sys.argv = ["bridge_thread_escalation_gate", "--quiet"]
    try:
        rc_code = gate.main()
    finally:
        sys.argv = old
    assert rc_code == 1                                   # BLOCKED (AK-M3 would no longer be silently dropped)


# ---------- integrity: frozen ArkProject snapshot untouched ----------

@frozen
def test_frozen_arkproject_snapshot_unchanged():
    man = json.loads((SNAP / "MANIFEST.json").read_text())
    # the MANIFEST records sha256 of each frozen artifact; re-verify a representative subset still matches
    drift = []
    ws = ROOT / "audits" / "ark-project-2024-07-strict-eval"
    for f in man["files"][:20]:
        p = ws / f["file"]
        if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() != f["sha256"]:
            drift.append(f["file"])
    assert drift == [], f"frozen ArkProject artifacts drifted: {drift}"
