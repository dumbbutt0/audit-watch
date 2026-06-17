"""Recall Lab regression — reasoning-gap sections reincorporated from the Cap eval (cap-2025-07-eval),
the first INGESTED full-coverage-experiment contest. 6 genuinely-new generalizable classes (delegated-yield
stablecoin + Symbiotic restaking) + the over-retraction discipline (M-5/C-08).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _md(name):
    return (ROOT / "agents" / name).read_text()


def test_cap_logic_sections():
    t = _md("logic.md")
    assert "cap M-1" in t and "STALE intermediate state" in t          # liquidation window close on stale health
    assert "cap M-6" in t and "instead of ONE" in t                     # multiplier default 0 not 1e27


def test_cap_dos_pause_blocks_derisk():
    t = _md("dos.md")
    assert "cap M-4" in t
    assert "de-risking" in t and "liquidat" in t.lower()


def test_cap_economic_sections():
    t = _md("economic_attack.md")
    assert "cap M-8" in t and "swept" in t.lower()                      # stranded reward swept by next caller
    assert "cap M-10" in t and "bonus" in t.lower()                     # liquidation sizing ignores bonus


def test_cap_token_integration_zero_amount():
    t = _md("token_integration.md")
    assert "cap M-3" in t and "InsufficientReward" in t


def test_over_retraction_discipline_in_skill():
    s = (ROOT / ".claude" / "skills" / "recall-lab" / "SKILL.md").read_text()
    assert "over-retraction" in s.lower()
    assert "C-08" in s and "slashTimestamp" in s


def test_cap_classes_registered():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    for slug, agent in [("stale-intermediate-state-gate", "logic"),
                        ("multiplier-default-zero-not-one", "logic"),
                        ("pause-blocks-derisk-path", "dos"),
                        ("stranded-reward-swept-by-next-caller", "economic_attack"),
                        ("liquidation-sizing-ignores-bonus", "economic_attack"),
                        ("zero-amount-external-call-reverts", "token_integration")]:
        assert slug in c, slug
        assert c[slug]["agent"] == agent and c[slug]["status"] == "reincorporated"
        assert any("cap-2025-07-eval" in e for e in c[slug]["awarded_examples"])
