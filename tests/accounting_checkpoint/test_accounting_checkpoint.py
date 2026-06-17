"""P249 — accounting examine-time checkpoint unit tests (A1-A5 detection + checkpoint-not-detector invariant)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import accounting_checkpoint_taxonomy as act  # noqa: E402

PAT = json.loads((ROOT / "config" / "accounting_checkpoint_patterns.json").read_text())


def _fams(name, body):
    return {r["accounting_family"] for r in act.classify("C", name, "", body, patterns=PAT)}


def test_a1_rounding_direction():
    body = "function previewWithdraw() { shares = assets.mulDiv(price, ONE, Rounding.Down); }"
    assert "A1_rounding_direction" in _fams("previewWithdraw", body)


def test_a2_conservation():
    body = "function settle() { _mint(a, x); _burn(b, y); uint left = amount - fee; }"
    assert "A2_conservation" in _fams("settle", body)


def test_a3_double_counting():
    body = "function _lock() { uint quantity = _quantity + remainder; lockedToken.quantity += _quantity; }"
    assert "A3_double_counting" in _fams("_lock", body)


def test_a4_shared_balance_depletion():
    body = "function deposit() { lpool.transferFrom(address(escrow), user, shares); pool -= shares; }"
    assert "A4_shared_balance_depletion" in _fams("deposit", body)


def test_a5_index_arithmetic_exactness():
    body = "function slice() { uint length = end - start; for (uint i; i < length; i++) {} }"
    assert "A5_index_arithmetic_exactness" in _fams("slice", body)


def test_checkpoint_never_concludes_or_sets_severity():
    """The architectural invariant: records are interrogative — no severity/confidence/verdict, ever."""
    body = "function withdraw() { x = a.mulDiv(p, ONE, Rounding.Down); _burn(u, s); }"
    recs = act.classify("C", "withdraw", "", body, patterns=PAT)
    assert recs, "expected at least one reasoning record"
    for r in recs:
        assert r["severity"] is None and r["confidence"] is None
        assert r["concluded"] is False and r["requires_operator_reasoning"] is True
        assert r["output_type"] == "reasoning_record"
        assert r["exploit_hypothesis"] == ""          # empty until operator answers
        assert len(r["questions"]) == 6


def test_benign_pure_view_emits_nothing():
    """A plain getter with no accounting op shape produces no record (no broad noise)."""
    body = "function owner() public view returns (address) { return _owner; }"
    assert _fams("owner", body) == set()


def test_only_five_families_exist():
    assert set(act.FAMILIES) == {
        "A1_rounding_direction", "A2_conservation", "A3_double_counting",
        "A4_shared_balance_depletion", "A5_index_arithmetic_exactness"}
