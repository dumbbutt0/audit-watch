"""Rust recall-lab iteration 2 (Orderly Solana Vault, Sherlock #524) — recall rose 0.0 -> 0.667.
Locks: the WOOFi-earned solana-missing-anchor-constraint class carries the Orderly cross-program examples,
a new lz-ordered-execution-option-missing class + specialist §6 were authored for the one miss, the
adjudication is language:rust (off the Solidity scoreboard) with recall_of_surfaced==0.667.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_orderly_cross_program_examples_on_earned_class():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    mac = c["solana-missing-anchor-constraint"]
    assert mac["status"] == "reincorporated" and mac["language"] == "rust"
    # the same class now carries examples from TWO different programs (transfer, not memorization)
    for e in ("woofi-solana-2024-08-eval:H-2",
              "orderly-solana-2024-10-eval:H-1", "orderly-solana-2024-10-eval:H-2"):
        assert e in mac["awarded_examples"], e


def test_lz_ordered_execution_class_added():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    k = "lz-ordered-execution-option-missing"
    assert k in c
    assert c[k]["status"] == "reincorporated" and c[k]["language"] == "rust"
    assert "orderly-solana-2024-10-eval:M-1" in c[k]["awarded_examples"]


def test_lz_specialist_section_authored():
    cpi = (ROOT / "agents" / "solana_cpi.md").read_text()
    assert "§6" in cpi and "addExecutorOrderedExecutionOption" in cpi and "inbound_nonce" in cpi
    am = (ROOT / "agents" / "solana_account_model.md").read_text()
    assert "lz_receive" in am and "allowed_token.mint_account" in am  # Orderly H-1/H-2 anchors


def test_orderly_adjudication_rust_and_recall():
    adj = json.loads((ROOT / "audits" / "orderly-solana-2024-10-eval" / "output" /
                      "eval_ready" / "adjudication.json").read_text())
    assert adj["language"] == "rust"
    assert adj["summary"]["recall_of_surfaced"] == 0.667
    assert adj["summary"]["by_label"]["STRONG"] == 2 and adj["summary"]["by_label"]["MISSED"] == 1
