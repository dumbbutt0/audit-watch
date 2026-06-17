"""
Recall 2025-02 miss-class replay (reconstructed). Proves each miss class now triggers the new
detection/routing, using the reconstructed fixtures under tests/fixtures/recall_miss_class/. Also verifies
the frozen Recall eval snapshot is NOT mutated (hash check only). Never re-scores the frozen eval.
"""
import hashlib
import importlib
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
FIX = ROOT / "tests" / "fixtures" / "recall_miss_class"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
cfi = importlib.import_module("cross_function_invariant_taxonomy")
asc = importlib.import_module("asset_source_consistency_taxonomy")
cl = importlib.import_module("checkpoint_liveness_taxonomy")
sft = importlib.import_module("special_focus_terms")
sweep_write = importlib.import_module("coverage_sweep_write")


def _fn(path: str, name: str) -> str:
    """Extract a function body block by name from a fixture .sol (brace-naive: to next blank-ish boundary)."""
    text = (FIX / path).read_text()
    # brace-naive: capture from the signature to the first closing brace (bodies are flat or the
    # discriminating signals appear before any nested brace) — avoids spilling into the sibling function.
    m = re.search(rf"function\s+{name}\b[^{{]*\{{[^}}]*\}}", text, re.DOTALL)
    return (m.group(0) if m else text)


# ---------- H-03: store-key vs read-key (cross_function_invariant) ----------

def test_h03_writer_reader_use_different_keys():
    w = cfi.classify("commitMessage", snippet=_fn("h03_hash_mismatch.sol", "commitMessage"))
    r = cfi.classify("consumeMessage", snippet=_fn("h03_hash_mismatch.sol", "consumeMessage"))
    assert "tohash" in w["key_calls"] and "totracingid" in r["key_calls"]    # divergence present in fixture


# ---------- H-04: counter exists without local limit (cross_function_invariant) ----------

def test_h04_increment_without_local_limit():
    c = cfi.classify("commitBottomUpMsg", snippet=_fn("h04_batch_count_overflow.sol", "commitBottomUpMsg"))
    assert c["has_counter_increment"] and not c["has_limit_check"]


# ---------- H-05: wrong asset source (asset_source_consistency) ----------

def test_h05_wrong_asset_source_high_risk():
    c = asc.classify("leave", snippet=_fn("h05_leave_wrong_asset.sol", "leave"))
    assert asc.is_high_risk(c) and "collateral" in c["families"] and "supply" in c["families"]


# ---------- H-06: cross-function reentrancy (guard locality) ----------

def test_h06_guarded_external_plus_unguarded_sibling():
    leave = cfi.classify("leave", snippet=_fn("h06_cross_function_reentrancy.sol", "leave"))
    sib = cfi.classify("addBootstrap", snippet=_fn("h06_cross_function_reentrancy.sol", "addBootstrap"))
    assert leave["has_reentrancy_guard"] and leave["has_external_call"]
    assert not sib["has_reentrancy_guard"]


# ---------- H-07: compaction skip (checkpoint_liveness + cross_function_invariant) ----------

def test_h07_compaction_loop_flagged():
    c = cl.classify("compact", snippet=_fn("h07_compact_index_skip.sol", "compact"))
    assert c["category"] == "compaction_skip" and cl.is_high_risk(c)


# ---------- H-08: permissionless register is special-focus → thin clear routed to needs_deep_pass ----------

def test_h08_register_is_special_focus_and_thin_clear_routed(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    (tmp_path / "output").mkdir(parents=True)
    (tmp_path / "data" / "coverage_sweep").mkdir(parents=True)
    it = {"id": "function:H08Gateway:register#01", "kind": "function", "contract": "H08Gateway",
          "file": "H08Gateway.sol", "name": "register",
          "signature": "function register(uint256 genesisCircSupply, uint256 collateral) external payable",
          "in_scope": True, "attack_surface_score": 4, "tags": [], "source_span": {}}
    assert sft.is_special_focus(it)                         # gateway/register/collateral terms
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "source": {}, "items": [it]}))
    (tmp_path / "output" / "coverage_dispositions.json").write_text(json.dumps({"dispositions": [{"manifest_id": it["id"], "status": "unassigned"}]}))
    (tmp_path / "data" / "coverage_sweep" / "_decisions.json").write_text(json.dumps({"decisions": [
        {"manifest_id": it["id"], "disposition": "cleared", "evidence_span": "H08Gateway.sol:1-5",
         "reason": "registration looks standard", "attacker_reachability": "any address",
         "guard_or_invariant": "none needed", "no_impact_reason": "just records stake"}]}))
    old = sys.argv; sys.argv = ["coverage_sweep_write"]
    try:
        sweep_write.main()
    finally:
        sys.argv = old
    d = json.loads((tmp_path / "output" / "coverage_dispositions.json").read_text())["dispositions"]
    assert d[0]["status"] == "assigned"                     # thin clear on register → needs_deep_pass


# ---------- H-09 / M-04: liveness ----------

def test_h09_recipient_call_in_loop_flagged():
    c = cl.classify("execBottomUpMsgs", snippet=_fn("h09_recipient_blocks_checkpoint.sol", "execBottomUpMsgs"),
                    contract="H09")
    assert c["liveness_sensitive"] and cl.is_high_risk(c)


def test_m04_flooding_flagged():
    c = cl.classify("stake", snippet=_fn("m04_flooding_confirmchange.sol", "stake"), contract="M04")
    assert c["category"] == "floodable_state"


# ---------- safe equivalents are NOT high-risk (no FP) ----------

def test_safe_equivalents_not_flagged():
    h05_safe = asc.classify("leave", snippet="function leave() external { uint256 amount = genesisBalance[msg.sender]; supplySource.transferFunds(msg.sender, amount); }")
    # single asset domain on the transfer path → not the H-05 cross-family payout shape
    assert not (h05_safe["asset_source_sensitive"] and "collateral" in h05_safe["families"])
    h09_safe = cl.classify("execBottomUpMsgs", snippet="function execBottomUpMsgs(Msg[] msgs) external { for (uint i;i<msgs.length;){ (bool ok,)=msgs[i].to.call{gas:100000}(\"\"); ok; unchecked{++i;} } }", contract="Safe")
    assert h09_safe["has_returndata_load"] is False


# ---------- integrity: frozen Recall snapshot untouched ----------

SNAP = ROOT / "audits" / "recall-2025-02-strict-eval" / "output" / "pre_answer_key_snapshot"
frozen = pytest.mark.skipif(not (SNAP / "MANIFEST.json").exists(), reason="frozen Recall snapshot not present")


@frozen
def test_frozen_recall_snapshot_unchanged():
    man = json.loads((SNAP / "MANIFEST.json").read_text())
    ws = ROOT / "audits" / "recall-2025-02-strict-eval"
    drift = []
    missing = []
    for f in man["files"]:
        p = ws / f["file"]
        if not p.is_file():
            missing.append(f["file"])
        elif hashlib.sha256(p.read_bytes()).hexdigest() != f["sha256"]:
            drift.append(f["file"])
    if missing:
        pytest.skip(f"frozen set incomplete in this checkout ({len(missing)} pinned artifacts archived to "
                    f"_eval_archive_*.tar.gz; restore to re-enable the guard)")
    assert drift == [], f"frozen Recall artifacts drifted: {drift}"
