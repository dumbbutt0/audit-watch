"""Rust recall-lab validation V1 (LayerZero V2 Solana endpoint, Zellic 2024) — NON-BLIND reincorporation.
Locks: 3 seeded classes upgraded to reincorporated with LZ evidence + 1 new DoS class, specialist sections
authored, all language:rust (off the Solidity scoreboard), and the scoreboard row is marked non-blind.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EX = "lz-solana-endpoint-zellic-2024"


def test_lz_classes_reincorporated_with_evidence():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    expect = {
        "solana-account-substitution-confusion": f"{EX}:H-3.2",
        "solana-remaining-accounts-trust": f"{EX}:M-3.3",
        "solana-close-account-revival": f"{EX}:H-3.1",
        "solana-account-count-config-mismatch-panic": f"{EX}:M-3.3",
    }
    for slug, ev in expect.items():
        assert slug in c, slug
        assert c[slug]["status"] == "reincorporated", slug
        assert c[slug]["language"] == "rust", slug
        assert ev in c[slug]["awarded_examples"], slug


def test_lz_specialist_sections():
    cpi = (ROOT / "agents" / "solana_cpi.md").read_text()
    assert "§7" in cpi and "re-validate" in cpi.lower() and "data_is_empty" in cpi   # F3.2
    assert "count-config-mismatch-panic" in cpi or "COUNT sub-check" in cpi          # F3.3
    am = (ROOT / "agents" / "solana_account_model.md").read_text()
    assert "Close-AUTHORITY" in am and "close_verify" not in am.lower() or "H-3.1" in am  # F3.1 anchor


def test_lz_scoreboard_marked_non_blind():
    sb = (ROOT / "evals" / "rust_scoreboard.md").read_text()
    assert "NON-BLIND" in sb and "not banked" in sb.lower() and EX in sb


def test_new_dos_class_is_rust_not_solana_prefixed_but_tagged():
    # the new class isn't solana-* prefixed-only logic; ensure it's rust-tagged so it stays off Solidity scoreboard
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    assert c["solana-account-count-config-mismatch-panic"]["language"] == "rust"
