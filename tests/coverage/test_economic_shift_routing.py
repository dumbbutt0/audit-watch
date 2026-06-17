"""
Tests for economic bit-shift routing in the math-estimator taxonomy (no LLM, no network).

A Solidity bit shift (`<<`/`>>`) used for VALUE SCALING in an economic context must route to
math-estimator review (the Swan/Dria getFee `2 << difficulty` miss). Bit twiddling (bitmap/flag/mask/
permission/packed-storage) must NOT route unless an economic term ties the shift to value movement.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
me = importlib.import_module("math_estimator_taxonomy")
validator = importlib.import_module("validate_math_estimator_clears")
sweep_write = importlib.import_module("coverage_sweep_write")


def _sensitive(name, snippet, signature=""):
    return me.classify(name, signature, snippet=snippet)["math_estimator_sensitive"]


# ---------- the 6 required fixtures ----------

def test_fee_shift_by_difficulty_is_sensitive():
    assert _sensitive("getFee", "uint256 diff = 2 << difficulty; fee = diff * generationFee;") is True


def test_reward_multiplier_shift_is_sensitive():
    assert _sensitive("rewardMultiplier", "rewardMultiplier = base << tier;") is True


def test_bitmap_one_shift_index_not_sensitive():
    assert _sensitive("buildBitmap", "bitmap = 1 << index;") is False


def test_role_mask_flags_shift_not_sensitive():
    assert _sensitive("computeRoleMask", "roleMask = flags << roleId;") is False


def test_gas_cost_shift_is_sensitive():
    assert _sensitive("gasCost", "gasCost = baseGas << multiplier;") is True


def test_packed_storage_shift_no_economic_not_sensitive():
    assert _sensitive("packSlot", "packedSlot = value << 8;") is False


# ---------- negative controls (FP backbone intact) ----------

def test_plain_economic_arithmetic_without_shift_not_sensitive():
    # economic terms present but NO shift → economic-shift branch must not fire
    assert _sensitive("transfer", "balances[to] += amount; fee = price * rate;") is False


def test_flag_shift_by_one_idiom_not_sensitive():
    # `flags << 1` bit-twiddle: bitmask word + not economic
    assert _sensitive("setFlag", "flags = flags << 1;") is False


def test_economic_term_substring_does_not_false_trigger():
    # 'rate' must not match inside 'generate'/'aggregate' (exact-token membership)
    assert _sensitive("generate", "uint256 x = seed << salt; aggregate(x);") is False


def test_plain_shift_with_economic_term_is_sensitive():
    assert _sensitive("priceFor", "p = price << exp;") is True


# ---------- writer routing (reuses existing strict/advisory machinery) ----------

@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _write(ws, rel, obj):
    p = ws / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2))
    return p


def _run(mod, argv):
    old = sys.argv
    sys.argv = [mod.__name__] + argv
    try:
        return mod.main()
    finally:
        sys.argv = old


def _ws_getfee_shift(ws, proof=None):
    item = {"id": "function:LLMOracleManager:getFee#shift", "kind": "function", "contract": "LLMOracleManager",
            "file": "Fee.sol", "name": "getFee",
            "signature": "function getFee() public view returns (uint256) { uint256 diff = 2 << difficulty; }",
            "in_scope": True, "attack_surface_score": 4, "tags": ["fee"],
            "source_span": {"start_line": 1, "end_line": 1}}
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [item]})
    disp = {"manifest_id": item["id"], "status": "cleared", "evidence": ["Fee.sol:1"], "finding_refs": [],
            "clear_reason": "Re-derived: diff=2<<difficulty"}
    if proof:
        disp["math_estimator_proof"] = proof
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [disp]})


def test_shift_scaling_clear_advisory_reports_strict_blocks(ws):
    _ws_getfee_shift(ws)  # proofless math-sensitive shift clear
    assert _run(validator, ["--mode", "advisory"]) == 0   # advisory never hard-fails
    out = json.loads((ws / "output" / "math_estimator_clear_validation.json").read_text())
    assert out["by_status"].get("missing_math_proof") == 1
    assert _run(validator, ["--mode", "strict"]) == 1     # strict blocks the proofless shift clear


def test_writer_routes_shift_clear_to_math_review_under_full_audit(ws, monkeypatch):
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        {"id": "function:LLMOracleManager:getFee#shift", "kind": "function", "contract": "LLMOracleManager",
         "file": "Fee.sol", "name": "getFee",
         "signature": "function getFee() public { uint256 diff = 2 << difficulty; fee = diff; }",
         "in_scope": True, "attack_surface_score": 4, "tags": ["fee"], "source_span": {"start_line": 1, "end_line": 1}}]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:LLMOracleManager:getFee#shift", "status": "unassigned",
         "evidence": [], "finding_refs": [], "clear_reason": None}]})
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [
        {"manifest_id": "function:LLMOracleManager:getFee#shift", "disposition": "cleared",
         "evidence_span": "Fee.sol:1", "reason": "fee math re-derived: diff=2<<difficulty",
         "attacker_reachability": "view fee quote", "guard_or_invariant": "onlyValidParameters",
         "no_impact_reason": "arithmetic"}]})  # no math_estimator_proof
    assert _run(sweep_write, []) == 0
    disp = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}
    item = disp["function:LLMOracleManager:getFee#shift"]
    assert item["status"] == "assigned"
    assert item["assigned_agent"] == "math_estimator_review"
