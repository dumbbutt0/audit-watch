"""Reincorporation of the generalizable particle (Solidity, full-coverage eval) reasoning-gap misses into the
production Solidity specialists. User directive 2026-06-12. 8 cross-protocol-general misses (6 hyper-specific
ones deliberately skipped). Solidity-tagged classes + specialist sections.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AID = "particle-2023-12-blind"


def test_particle_classes_reincorporated():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    expect = {
        "deadline-blocktimestamp-noop": "M-02",
        "missing-liquidity-slippage": "M-15",
        "global-param-change-affects-open-positions": "M-05",
        "reward-folded-into-liquidation-condition": "M-06",
        "stale-snapshot-before-mutation": "H-02",
        "ported-uni-0.8-underflow-revert": "H-04",
        "blacklist-token-push-refund-dos": "H-01",
        "act-on-unowned-external-asset": "M-12",
    }
    for slug, fid in expect.items():
        assert slug in c, slug
        assert c[slug]["status"] == "reincorporated", slug
        assert c[slug].get("language", "solidity") == "solidity", slug
        assert f"{AID}:{fid}" in c[slug]["awarded_examples"], slug


def test_particle_specialist_sections():
    logic = (ROOT / "agents" / "logic.md").read_text()
    for s in ("§30", "§31", "§32", "§33", "§34"):
        assert s in logic, s
    assert "deadline: block.timestamp" in logic and "amountMin" in logic
    arith = (ROOT / "agents" / "arithmetic.md").read_text()
    assert "unchecked" in arith and "particle H-04" in arith
    dos = (ROOT / "agents" / "dos.md").read_text()
    assert "§17" in dos and "blacklist" in dos.lower()
    ac = (ROOT / "agents" / "access_control.md").read_text()
    assert "particle M-12" in ac and "ownership" in ac.lower()
