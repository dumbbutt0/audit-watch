"""Rust recall-lab validation V2 (Drift Protocol, Zellic) — NON-BLIND harvest.
Locks: new Anchor-IDL class + strengthened arithmetic (division) class, both rust-tagged, specialist §10.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EX = "drift-zellic-2022"


def test_anchor_idl_class_added():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    k = "solana-anchor-idl-instructions-enabled"
    assert k in c and c[k]["status"] == "reincorporated" and c[k]["language"] == "rust"
    assert f"{EX}:anchor-idl-enabled" in c[k]["awarded_examples"]


def test_arithmetic_division_strengthened():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    a = c["solana-arithmetic-unchecked"]
    assert a["language"] == "rust"
    assert f"{EX}:unchecked-division" in a["awarded_examples"]
    assert "checked_div" in a["description"] or "DIVISION" in a["description"]


def test_idl_specialist_section():
    am = (ROOT / "agents" / "solana_account_model.md").read_text()
    assert "IDL" in am and "no-default-idl" in am
    assert "DIVISION sub-checks" in am
