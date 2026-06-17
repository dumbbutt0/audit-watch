"""Recall Lab regression — the one genuinely-new Solidity reasoning-gap section from the zetachain eval
(zetachain-2023-10-holdout, loop iteration). The other 47 misses are Go/observer-node findings outside
Solidity scope (coverage-gap, not prompt-addressable). H-10 = wrong DEX-router method -> swap always reverts.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_wrong_router_method_section_present():
    t = (ROOT / "agents" / "token_integration.md").read_text()
    assert "zetachain H-10" in t
    assert "always revert" in t
    assert "exactInputSingle" in t
    assert "actual ABI" in t


def test_wrong_router_method_class_registered():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    slug = "wrong-router-method-integration-revert"
    assert slug in c
    assert c[slug]["agent"] == "token_integration"
    assert c[slug]["status"] == "reincorporated"
    assert any("zetachain" in e for e in c[slug]["awarded_examples"])
