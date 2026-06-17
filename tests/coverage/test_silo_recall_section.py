"""Recall Lab regression — the one genuinely-new (uncovered) section from the silo eval
(silo-finance-2025-03-strict-eval M-03): approve(_,0) reverts for some tokens, bricking a market-removal/
teardown path. Sibling of the existing transfer-on-zero-revert section. Silo's other misses were SAME_AREA
to already-covered classes (feeShares order, ERC4626 rounding, slippage, reward accrual).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_approve_zero_section_present():
    t = (ROOT / "agents" / "token_integration.md").read_text()
    assert "silo M-03" in t
    assert "approve" in t.lower() and "zero approval" in t
    assert "teardown" in t.lower() or "removal" in t.lower()


def test_approve_zero_class_registered():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    slug = "approve-zero-reverts-blocks-teardown"
    assert slug in c and c[slug]["agent"] == "token_integration"
    assert c[slug]["status"] == "reincorporated"
    assert any("silo" in e for e in c[slug]["awarded_examples"])
