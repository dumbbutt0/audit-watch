"""Reincorporation of the iq-ai (Solidity, full-coverage eval) reasoning-gap miss (OZ quorum-fraction
percent semantics) into the production Solidity specialist. User directive 2026-06-12."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_oz_quorum_class_reincorporated():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    k = "oz-quorum-fraction-percent-misuse"
    assert k in c and c[k]["status"] == "reincorporated" and c[k].get("language", "solidity") == "solidity"
    assert "iq-ai-2025-01-blind:H-01" in c[k]["awarded_examples"]


def test_oz_quorum_specialist_section():
    ac = (ROOT / "agents" / "access_control.md").read_text()
    assert "GovernorVotesQuorumFraction" in ac and "iq-ai H-01" in ac
    assert "N%" in ac or "N PERCENT" in ac
