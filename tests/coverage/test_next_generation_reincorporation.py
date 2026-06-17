"""Recall-lab: Next Generation (C4 2025-01) FRESH BLIND Solidity audit. The blind hand pass caught the High
(NG-01 <-> H-01 cross-chain domainSeparator replay) + M-02 (approve skips blacklist), and MISSED M-01
(fee charged outside the approved allowance) + M-03 (forwarder request has no deadline). This locks the two
miss reincorporations so future runs don't repeat them."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_miss_classes_reincorporated():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    for slug, fid in (("fee-charged-outside-allowance", "next-generation-2025-01-blind:M-01"),
                      ("forwarder-request-missing-deadline", "next-generation-2025-01-blind:M-03")):
        assert slug in c, slug
        assert c[slug]["status"] == "reincorporated" and c[slug]["language"] == "solidity"
        assert fid in c[slug]["awarded_examples"], slug


def test_specialist_sections_authored():
    ti = (ROOT / "agents" / "token_integration.md").read_text()
    assert "fee-charged-outside-allowance" in ti and "transferFrom" in ti and "allowance" in ti.lower()
    ac = (ROOT / "agents" / "access_control.md").read_text()
    assert "forwarder-request-missing-deadline" in ac and "ForwardRequest" in ac and "deadline" in ac.lower()


def test_garden_unchecked_approve_reincorporated():
    """Garden (C4 2025-11) blind miss: M-01 unchecked approve() in UDA.sol -> reincorporated."""
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    k = c.get("unchecked-erc20-approve-return", {})
    assert k.get("status") == "reincorporated" and k.get("language") == "solidity"
    assert "garden-2025-11-blind:M-01" in k.get("awarded_examples", [])
    assert "description" in k and "agent" in k  # full schema (pattern_checklist needs description)
    ti = (ROOT / "agents" / "token_integration.md").read_text()
    assert "unchecked-erc20-approve-return" in ti and "SafeERC20" in ti and "forceApprove" in ti
