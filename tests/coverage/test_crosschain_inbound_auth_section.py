"""Recall Lab regression — the one genuinely-new cross-chain section drained from the training tail
(centrifuge M-01 + decent M-03). The gap: cross_chain.md covered replay/proof/dest-gas/refund-recipient
but NOT inbound message SOURCE authentication (caller endpoint + trusted-remote (srcChain,srcAddr)).
Most other tail misses (DAI permit, dest-gas, refund-recipient, fee-bypass-via-direct-call) were already covered.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_inbound_source_auth_section_present():
    t = (ROOT / "agents" / "cross_chain.md").read_text()
    assert "centrifuge M-01 + decent M-03" in t
    assert "AUTHENTICATE THE SOURCE" in t
    assert "trusted-remote" in t
    assert "receiveFromBridge" in t


def test_inbound_source_auth_class_registered():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    slug = "cross-chain-inbound-source-unauthenticated"
    assert slug in c
    assert c[slug]["agent"] == "cross_chain"
    assert c[slug]["status"] == "reincorporated"
    ex = c[slug]["awarded_examples"]
    assert any("centrifuge" in e for e in ex) and any("decent" in e for e in ex)
