"""Rust recall-lab iteration 1 (WOOFi Solana) — 5 reasoning-gap misses reincorporated. Locks: 2 seeded
classes upgraded to reincorporated with WOOFi evidence, 3 new Solana classes added, specialist sections authored.
All language:rust (kept off the Solidity scoreboard).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_woofi_classes_reincorporated():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    expect = {
        "solana-missing-anchor-constraint": "H-2",
        "solana-missing-signer-check": "M-2",
        "solana-pda-signer-seeds-missing-bump": "H-1",
        "solana-init-authority-mismatch-vs-use": "M-1",
        "solana-duplicate-mutable-account-serialization": "M-3",
    }
    for slug, fid in expect.items():
        assert slug in c, slug
        assert c[slug]["status"] == "reincorporated", slug
        assert c[slug]["language"] == "rust", slug
        assert any(f"woofi-solana-2024-08-eval:{fid}" == e for e in c[slug]["awarded_examples"]), slug


def test_woofi_specialist_sections():
    am = (ROOT / "agents" / "solana_account_model.md").read_text()
    assert "solana-init-authority-mismatch-vs-use" in am and "create_rebate_info" in am
    assert "solana-duplicate-mutable-account-serialization" in am and "woopool_quote" in am
    cpi = (ROOT / "agents" / "solana_cpi.md").read_text()
    assert "solana-pda-signer-seeds-missing-bump" in cpi and "bump" in cpi.lower()


def test_rust_scoreboard_separate_from_solidity():
    assert (ROOT / "evals" / "rust_scoreboard.md").exists()
    # the WOOFi adjudication is rust + must not be in the Solidity-language set
    adj = json.loads((ROOT / "audits" / "woofi-solana-2024-08-eval" / "output" / "eval_ready" / "adjudication.json").read_text())
    assert adj["language"] == "rust" and adj["summary"]["recall_of_surfaced"] == 0.0
