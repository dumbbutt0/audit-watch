"""Reincorporation of the 2 NOVEL nudgexyz (Solidity, full-coverage eval) reasoning-gap misses into the
production Solidity specialists + the checklist pass. User directive 2026-06-12 ("Pls reincorporate the misses").

  M-03  aa-wallet-cross-chain-address  -> cross_chain.md   (AA wallets have a different address per chain,
                                                            so cross-chain reward attribution loses funds)
  M-04  tx-initiator-not-verified      -> access_control.md (trusted relayer forwards an unbound beneficiary
                                                            -> attacker routes the full reward to a UniV2 pool)

Both were MISSED because they were outside the reincorporated pattern library; this closes the novel->known
loop by also adding scan signals so they become checklist-flaggable on future passes.
"""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))


def _classes():
    return json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]


def test_aa_wallet_class_reincorporated():
    c = _classes()
    k = "aa-wallet-cross-chain-address"
    assert k in c and c[k]["status"] == "reincorporated"
    assert c[k].get("language", "solidity") == "solidity"
    assert c[k]["agent"] == "cross_chain"
    assert "nudgexyz-2025-03-blind:M-03" in c[k]["awarded_examples"]


def test_tx_initiator_class_reincorporated():
    c = _classes()
    k = "tx-initiator-not-verified"
    assert k in c and c[k]["status"] == "reincorporated"
    assert c[k].get("language", "solidity") == "solidity"
    assert c[k]["agent"] == "access_control"
    assert "nudgexyz-2025-03-blind:M-04" in c[k]["awarded_examples"]


def test_specialist_sections_authored():
    cc = (ROOT / "agents" / "cross_chain.md").read_text()
    assert "aa-wallet-cross-chain-address" in cc and "nudgexyz-2025-03 M-03" in cc
    assert "different" in cc.lower() and "EOA" in cc
    ac = (ROOT / "agents" / "access_control.md").read_text()
    assert "tx-initiator-not-verified" in ac and "nudgexyz-2025-03 M-04" in ac
    assert "beneficiary" in ac.lower() and "relayer" in ac.lower()


def test_scan_signals_flag_the_missed_sites():
    """Both novel patterns must now be checklist-flaggable: the scan must fire on the exact missed
    nudgexyz loci (handleReallocation + the relayed userAddress param)."""
    import pattern_checklist
    out = pattern_checklist.build("nudgexyz-2025-03-blind")
    txt = out.read_text()
    assert "language: solidity" in txt
    assert "tx-initiator-not-verified" in txt
    assert "aa-wallet-cross-chain-address" in txt
    # the actual missed function must be surfaced as a candidate site
    assert "handleReallocation" in txt
