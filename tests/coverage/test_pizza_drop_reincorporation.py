"""Recall-lab: Pizza Drop (CodeHawks 2025-08-aptos-pizza-drop) FRESH BLIND move/APTOS audit #2.
Blind recall 1.00 — caught all 3 awarded mechanisms (H-01 access-control bypass via unguarded entry,
H-02 reward in Octas-not-APT units, M-01 predictable timestamp randomness). Severity calibration was
imperfect on two (H-02 rated Medium, M-01 rated High) but the bug classes were all surfaced.

H-01 (access bypass) is covered by the existing move capability/visibility sections (#1/#7/#8) and
H-02 (units) by the units/decimals lens, so no NEW section for those. M-01 (predictable randomness)
had ZERO coverage in ANY agent, so it is reincorporated as a durable general-Move lens:
move-insecure-onchain-randomness -> move_object_capability.md#10 (predictability + Aptos
test-and-abort biasing)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_pizza_drop_randomness_class():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    slug = "move-insecure-onchain-randomness"
    assert slug in c and c[slug]["status"] == "reincorporated"
    assert "pizza-drop-aptos-2025-08-blind:M-01" in c[slug]["awarded_examples"]
    assert c[slug]["language"] == "move"
    assert c[slug]["agent"] == "move_object_capability"


def test_pizza_drop_randomness_section():
    mc = (ROOT / "agents" / "move_object_capability.md").read_text()
    assert "move-insecure-onchain-randomness" in mc
    # predictability mode
    assert "timestamp::now" in mc and "predictab" in mc.lower()
    # test-and-abort / selective-abort biasing mode
    assert "test-and-abort" in mc.lower() or "selective abort" in mc.lower()
    assert "randomness" in mc.lower()
