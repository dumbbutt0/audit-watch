"""Rust recall-lab iteration 3 (Pyth Lazer Solana, Zellic) — GENUINE-BLIND firm-report, recall 1.0.
Locks: the ed25519-introspection class added + reinit example, the adjudication is blind+rust+recall 1.0,
specialist §8 authored, and it's off the Solidity scoreboard.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AID = "pyth-lazer-solana-2024-eval"


def test_ed25519_introspection_class_added():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    k = "solana-ed25519-introspection-data-unbound"
    assert k in c and c[k]["status"] == "reincorporated" and c[k]["language"] == "rust"
    assert f"{AID}:3.1" in c[k]["awarded_examples"]
    # reinit class carries the 3.2 example
    assert f"{AID}:3.2" in c["solana-reinit-missing-init-guard"]["awarded_examples"]


def test_specialist_section_8():
    cpi = (ROOT / "agents" / "solana_cpi.md").read_text()
    assert "§8" in cpi and "ed25519" in cpi.lower() and "message_offset" in cpi


def test_pyth_adjudication_blind_rust_recall_1():
    adj = json.loads((ROOT / "audits" / AID / "output" / "eval_ready" / "adjudication.json").read_text())
    assert adj["language"] == "rust"
    assert adj["summary"]["recall_of_surfaced"] == 1.0
    assert adj["summary"]["blind"] is True and adj.get("source") == "firm-report"
    assert adj["summary"]["by_label"]["STRONG"] == 2 and adj["summary"]["by_label"]["MISSED"] == 0
