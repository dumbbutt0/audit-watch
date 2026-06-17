"""Checklist pass — targets the 'having the class != applying it' weakness (secondswap M-13: a reincorporated
pattern existed but was missed). The checklist actively scans the audit source for reincorporated-pattern
anchors and surfaces candidate sites. Locks: it generates, it's language-filtered, and it surfaces the
specific global-param-change site (setMarketplace) that was missed.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))


def test_checklist_generates_and_is_language_filtered():
    import pattern_checklist
    out = pattern_checklist.build("secondswap-2024-12-blind")
    assert out.exists()
    txt = out.read_text()
    assert "Pattern checklist pass" in txt and "language: solidity" in txt
    assert "AUTO-SCANNED CANDIDATE SITES" in txt and "FULL CHECKLIST" in txt
    # solidity audit must NOT list rust-only classes in the full checklist
    assert "solana-" not in txt


def test_checklist_surfaces_the_missed_global_param_pattern():
    import pattern_checklist
    out = pattern_checklist.build("secondswap-2024-12-blind")
    txt = out.read_text()
    # the M-13 locus I missed (setMarketplace) must be flagged under the reincorporated pattern
    assert "global-param-change-affects-open-positions" in txt
    assert "setMarketplace" in txt


def test_checklist_rust_audit_filters_to_rust():
    import pattern_checklist
    out = pattern_checklist.build("pyth-lazer-solana-2024-eval")
    txt = out.read_text()
    assert "language: rust" in txt
    # rust checklist should reference solana classes, not solidity-only ones like neobase's
    assert "solana-" in txt
