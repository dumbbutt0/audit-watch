"""Reincorporation of the GENERALIZABLE phi (Solidity, full-coverage eval, 8th datapoint) reasoning-gap misses
into the production Solidity specialists. User directive 2026-06-12 ("reincorporate the misses"). These are subtle
reasoning bugs (signature scope, reentrancy nuance, pausable base, cached config, enumerable-map gas bloat,
post-commitment mutation) -> reincorporated as PROMPT KNOWLEDGE + mechanism classes, NOT FP-tight scan lenses
(per the kleidi/particle lesson). H-05 was already STRONG-caught; M-02/M-03 fold into existing classes
(division-as-percentage-fee / missing-slippage); M-04 protocol-specific (skipped).

  H-01      signature-missing-chainid-replay         -> access_control.md
  H-02+M-05 signature-scope-gap-unsigned-params      -> access_control.md
  H-03      map-entry-zeroed-not-removed-gas-dos     -> dos.md#19
  M-01      wrong-pausable-base-no-transfer-block    -> dos.md#20
  H-06      reentrancy-refund-before-state-finalize  -> reentrancy.md
  H-07+H-04 post-commitment-config-mutation          -> logic.md#39
  M-06      cached-config-not-refetched              -> logic.md#40
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

NEW_CLASSES = {
    "signature-missing-chainid-replay": ("access_control", "H-01"),
    "signature-scope-gap-unsigned-params": ("access_control", "H-02"),
    "map-entry-zeroed-not-removed-gas-dos": ("dos", "H-03"),
    "wrong-pausable-base-no-transfer-block": ("dos", "M-01"),
    "reentrancy-refund-before-state-finalize": ("reentrancy", "H-06"),
    "post-commitment-config-mutation": ("logic", "H-07"),
    "cached-config-not-refetched": ("logic", "M-06"),
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
        assert any(f"phi-2024-08-blind:{award}" == e for e in c[name]["awarded_examples"])


def test_specialist_sections_authored():
    ac = (ROOT / "agents" / "access_control.md").read_text()
    assert "signature-missing-chainid-replay" in ac and "phi-2024-08 H-01" in ac
    assert "signature-scope-gap-unsigned-params" in ac and "phi-2024-08 H-02" in ac
    dos = (ROOT / "agents" / "dos.md").read_text()
    assert "map-entry-zeroed-not-removed-gas-dos" in dos and "phi-2024-08 H-03" in dos
    assert "wrong-pausable-base-no-transfer-block" in dos and "phi-2024-08 M-01" in dos
    re = (ROOT / "agents" / "reentrancy.md").read_text()
    assert "reentrancy-refund-before-state-finalize" in re and "phi-2024-08 H-06" in re
    lg = (ROOT / "agents" / "logic.md").read_text()
    assert "post-commitment-config-mutation" in lg and "phi-2024-08 H-07" in lg
    assert "cached-config-not-refetched" in lg and "phi-2024-08 M-06" in lg


def test_no_rust_contamination():
    """All new classes must be solidity-tagged so they never enter the rust scoreboard."""
    c = _classes()
    for name in NEW_CLASSES:
        assert c[name].get("language") == "solidity"


def test_remaining_misses_reincorporated():
    """The 3 deliberately-deferred misses: M-02 -> its own new class; M-03 -> folded into the existing
    missing-slippage class as an awarded example; M-04 stays protocol-specific (no class)."""
    c = _classes()
    # M-02: distinct new class (wrong-unit sanity cap)
    assert "param-sanity-cap-wrong-unit" in c
    k = c["param-sanity-cap-wrong-unit"]
    assert k["status"] == "reincorporated" and k.get("language", "solidity") == "solidity"
    assert k["agent"] == "arithmetic"
    assert "phi-2024-08-blind:M-02" in k["awarded_examples"]
    ar = (ROOT / "agents" / "arithmetic.md").read_text()
    assert "param-sanity-cap-wrong-unit" in ar and "phi-2024-08 M-02" in ar
    # M-03: folded into the existing dynamic-price slippage class
    assert "phi-2024-08-blind:M-03" in c["missing-slippage-dynamic-price-op"]["awarded_examples"]
