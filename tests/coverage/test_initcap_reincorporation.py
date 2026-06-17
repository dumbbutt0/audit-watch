"""Reincorporation of the 3 init-capital (Solidity, full-coverage eval) reasoning-gap misses into the
production Solidity specialists. User directive 2026-06-12. Solidity-tagged classes + specialist sections.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AID = "init-capital-2024-01-blind"


def test_initcap_classes_reincorporated():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    expect = {
        "memory-copy-state-write-lost": "M-02",
        "unconditional-native-refund-dos": "M-01",
        "strict-equality-balance-dos": "M-03",
    }
    for slug, fid in expect.items():
        assert slug in c, slug
        assert c[slug]["status"] == "reincorporated", slug
        assert c[slug].get("language", "solidity") == "solidity", slug
        assert f"{AID}:{fid}" in c[slug]["awarded_examples"], slug


def test_initcap_specialist_sections():
    logic = (ROOT / "agents" / "logic.md").read_text()
    assert "§29" in logic and "init-capital M-02" in logic and "memory" in logic.lower()
    dos = (ROOT / "agents" / "dos.md").read_text()
    assert "§15" in dos and "§16" in dos
    assert "init-capital M-01" in dos and "init-capital M-03" in dos
    assert "refundNative" in dos and "balanceOf" in dos
