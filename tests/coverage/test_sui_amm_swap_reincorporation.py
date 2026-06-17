"""Recall Lab regression — the two genuinely-new Move reasoning-gap sections from the sui-amm-swap eval
(sui-amm-swap-2022-11-eval, Move loop iteration 1). Blind cold pass surfaced 5/7; the two misses were both
reasoning gaps (files opened, mechanism not flagged):
  M-1 = swap path never RE-ASSERTS the constant-product K invariant post-swap (the absent guard is the finding).
  M-4 = event-emit helpers are `public fun` -> anyone forges protocol events (visibility audit skipped emitters).
These tests lock the §7 sections + the two reincorporated move-* classes so the reincorporation can't silently
regress. Move classes are language:move and NEVER count toward Solidity/Rust recall.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_m1_constant_product_invariant_section_present():
    t = (ROOT / "agents" / "move_clmm_math.md").read_text()
    assert "move-constant-product-invariant-recheck" in t
    assert "post-mutation" in t.lower()
    # the core teaching: the missing guard is the finding even when current pricing is conservative
    assert "absent guard" in t.lower()
    assert "sui-amm-swap-2022-11-eval" in t


def test_m4_public_helper_visibility_section_present():
    t = (ROOT / "agents" / "move_object_capability.md").read_text()
    assert "move-public-helper-visibility" in t
    # the core teaching: an emit is a side effect, not a read
    assert "side effect, not a read" in t.lower()
    assert "forge protocol events" in t.lower()
    assert "sui-amm-swap-2022-11-eval" in t


def test_new_move_classes_registered_and_reincorporated():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    for slug, agent in (
        ("move-constant-product-invariant-recheck", "move_clmm_math"),
        ("move-public-helper-visibility", "move_object_capability"),
    ):
        assert slug in c, slug
        assert c[slug]["language"] == "move", slug
        assert c[slug]["status"] == "reincorporated", slug
        assert c[slug]["agent"] == agent, slug
        assert any("sui-amm-swap" in e for e in c[slug]["awarded_examples"]), slug
