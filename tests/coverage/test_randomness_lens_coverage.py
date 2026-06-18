"""Insecure on-chain randomness is now a CROSS-LANGUAGE lens family. It was first reincorporated for Move
(move-insecure-onchain-randomness, eval-anchored on pizza-drop M-01); this test pins the SEEDED extensions to
Solidity (economic_attack.md#12) and Solana (solana_account_model.md#11), generalized a-priori from the same
Move finding. Seeded => status 'seeded' + empty awarded_examples (NOT yet eval-validated for EVM/Solana; they
become 'reincorporated' only when a scored EVM/Solana contest confirms them)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _classes():
    return json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]


def test_evm_randomness_class_reincorporated():
    # EVM lens was validated on eggstravaganza H-01 (blind fleet, economic_attack cited §12) -> promoted.
    c = _classes()
    e = c["evm-insecure-onchain-randomness"]
    assert e["status"] == "reincorporated"
    assert "eggstravaganza-2025-04-blind:H-01" in e["awarded_examples"]
    assert e["language"] == "solidity"
    assert e["agent"] == "economic_attack"
    assert e["prompt_section"] == "economic_attack.md#12"
    assert e.get("description")


def test_solana_randomness_class_still_seeded():
    # Solana lens not yet eval-validated (no clonable Solana randomness contest found) -> honestly seeded.
    c = _classes()
    s = c["solana-insecure-onchain-randomness"]
    assert s["status"] == "seeded"
    assert s["awarded_examples"] == []
    assert s["language"] == "rust"
    assert s["agent"] == "solana_account_model"
    assert s["prompt_section"] == "solana_account_model.md#11"
    assert s.get("description")


def test_move_randomness_remains_reincorporated():
    # the cross-language family origin stays eval-anchored
    c = _classes()
    m = c["move-insecure-onchain-randomness"]
    assert m["status"] == "reincorporated"
    assert "pizza-drop-aptos-2025-08-blind:M-01" in m["awarded_examples"]


def test_evm_randomness_section_present():
    t = (ROOT / "agents" / "economic_attack.md").read_text()
    assert "evm-insecure-onchain-randomness" in t
    assert "block.timestamp" in t and "prevrandao" in t.lower()
    assert "blockhash" in t


def test_solana_randomness_section_present():
    t = (ROOT / "agents" / "solana_account_model.md").read_text()
    assert "solana-insecure-onchain-randomness" in t
    assert "Clock" in t and "slot" in t.lower()
    assert "SlotHashes" in t or "blockhash" in t.lower()
