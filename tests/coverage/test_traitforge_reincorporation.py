"""Reincorporation of the GENERALIZABLE traitforge (Solidity, full-coverage eval, 7th datapoint) reasoning-gap
misses into the production Solidity specialists + the checklist pass. User directive 2026-06-12 ("reincorporate
the misses"). Hyper-TraitForge-specific golden-god mechanics (M-05/M-06/M-09/M-19) and pure design/param-default
issues were deliberately SKIPPED per the no-noise discipline.

  H-03  division-as-percentage-fee                 -> arithmetic.md      (amount/feeParam != percentage)
  H-02  stale-owner-snapshot-reward-attribution    -> logic.md#35        (credit keyed on initialOwner, decremented by later holder)
  H-04  counter-reset-ignores-preexisting-entries  -> logic.md#36        (reset-to-0 wipes pre-seeded next-bucket count)
  H-05  cap-enforced-one-path-not-sibling          -> logic.md#37        (limit checked in one writer, not the sibling)
  M-01  read-before-init-zero-default              -> logic.md#38        (consume lazily-batched store before init)
  M-04+M-16 missing-slippage-dynamic-price-op      -> economic_attack.md (dynamic price/payout, no slippage bound)
  M-02  no-exit-path-fund-lockup                   -> dos.md#18          (sole exit gated on an unreachable condition)

The two cleanly-detectable patterns (H-03, H-02) also get scan signals so they become checklist-flaggable.
"""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

NEW_CLASSES = {
    "division-as-percentage-fee": ("arithmetic", "H-03"),
    "stale-owner-snapshot-reward-attribution": ("logic", "H-02"),
    "counter-reset-ignores-preexisting-entries": ("logic", "H-04"),
    "cap-enforced-one-path-not-sibling": ("logic", "H-05"),
    "read-before-init-zero-default": ("logic", "M-01"),
    "missing-slippage-dynamic-price-op": ("economic_attack", "M-04"),
    "no-exit-path-fund-lockup": ("dos", "M-02"),
}


def _classes():
    return json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]


def test_all_seven_classes_reincorporated():
    c = _classes()
    for name, (agent, award) in NEW_CLASSES.items():
        assert name in c, f"missing class {name}"
        assert c[name]["status"] == "reincorporated"
        assert c[name].get("language", "solidity") == "solidity", f"{name} must be solidity-tagged"
        assert c[name]["agent"] == agent
        assert any(f"traitforge-2024-07-blind:{award}" == e for e in c[name]["awarded_examples"])


def test_specialist_sections_authored():
    ar = (ROOT / "agents" / "arithmetic.md").read_text()
    assert "division-as-percentage-fee" in ar and "traitforge-2024-07 H-03" in ar
    lg = (ROOT / "agents" / "logic.md").read_text()
    for slug, marker in [
        ("stale-owner-snapshot-reward-attribution", "H-02"),
        ("counter-reset-ignores-preexisting-entries", "H-04"),
        ("cap-enforced-one-path-not-sibling", "H-05"),
        ("read-before-init-zero-default", "M-01"),
    ]:
        assert slug in lg and f"traitforge-2024-07 {marker}" in lg
    ea = (ROOT / "agents" / "economic_attack.md").read_text()
    assert "missing-slippage-dynamic-price-op" in ea and "M-04 + M-16" in ea
    dos = (ROOT / "agents" / "dos.md").read_text()
    assert "no-exit-path-fund-lockup" in dos and "traitforge-2024-07 M-02" in dos


def test_scan_signals_flag_the_detectable_missed_sites():
    """The two cleanly-detectable patterns must now be checklist-flaggable on the exact awarded loci."""
    import pattern_checklist
    out = pattern_checklist.build("traitforge-2024-07-blind")
    txt = out.read_text()
    assert "language: solidity" in txt
    assert "division-as-percentage-fee" in txt
    assert "stale-owner-snapshot-reward-attribution" in txt
    # the actual missed loci surfaced as candidate sites
    assert "taxCut" in txt
    assert "initialOwners" in txt
