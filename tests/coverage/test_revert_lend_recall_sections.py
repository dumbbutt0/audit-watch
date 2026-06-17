"""Recall Lab regression — genuinely-NEW reasoning-gap sections from the revert-lend eval
(revert-lend-2024-03-strict-eval, loop iteration 2). Most revert-lend awarded findings were already
reincorporated in p323 (H-02/H-05/M-01/M-25/M-27...); this locks ONLY the non-duplicate additions:
H-06 (callback revert-DoS variant), M-07 (oracle decimal overflow), M-03 (no min position size).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _md(name):
    return (ROOT / "agents" / name).read_text()


def test_h06_liquidation_dos_callback_variant_added_to_reentrancy():
    t = _md("reentrancy.md")
    assert "revert-lend H-06" in t
    assert "un-liquidatable" in t
    assert "DUAL IMPACT" in t  # DoS variant complements the existing H-02 reentrancy section


def test_m07_oracle_decimal_overflow_section():
    t = _md("oracle.md")
    assert "revert-lend M-07" in t
    assert "high-decimal" in t
    assert "mulDiv" in t


def test_m03_no_min_position_size_section():
    t = _md("economic_attack.md")
    assert "revert-lend M-03" in t
    assert "minimum loan" in t.lower() or "minimum debt" in t.lower()
    assert "bad debt" in t


def test_revert_lend_classes_registered():
    classes = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    for slug, agent in [("position-nft-callback-liquidation-dos", "reentrancy"),
                        ("oracle-decimal-scaling-overflow", "oracle"),
                        ("no-min-position-size-dust-baddebt", "economic_attack")]:
        assert slug in classes, slug
        assert classes[slug]["agent"] == agent
        assert classes[slug]["status"] == "reincorporated"
        assert any("revert-lend" in e for e in classes[slug]["awarded_examples"])
