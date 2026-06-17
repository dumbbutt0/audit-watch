"""Reincorporation of the 5 neobase (Solidity, full-coverage eval) reasoning-gap misses into the production
Solidity specialists. User directive 2026-06-12. Locks: 5 solidity-tagged reincorporated classes with neobase
examples + the specialist sections authored. These are Solidity classes (must NOT be rust-tagged).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AID = "neobase-2024-03-blind"


def test_neobase_classes_reincorporated():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    expect = {
        "vote-power-stranded-on-gauge-removal": "H-01",
        "slope-underflow-dos": "M-01",
        "governance-weight-override": "M-03",
        "masterchef-rewarddebt-rounding": "M-05",
        "unlock-override-free-vote": "M-07",
    }
    for slug, fid in expect.items():
        assert slug in c, slug
        assert c[slug]["status"] == "reincorporated", slug
        assert c[slug].get("language", "solidity") == "solidity", slug  # Solidity, NOT rust
        assert f"{AID}:{fid}" in c[slug]["awarded_examples"], slug


def test_neobase_specialist_sections():
    logic = (ROOT / "agents" / "logic.md").read_text()
    assert "§26" in logic and "§27" in logic and "§28" in logic
    assert "neobase H-01" in logic and "neobase M-03" in logic and "neobase M-07" in logic
    dos = (ROOT / "agents" / "dos.md").read_text()
    assert "§14" in dos and "neobase M-01" in dos and "slope -= " in dos.replace("`", "")
    econ = (ROOT / "agents" / "economic_attack.md").read_text()
    assert "§10" in econ and "neobase M-05" in econ and "rewardDebt" in econ
