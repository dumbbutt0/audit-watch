"""Recall-lab: Pump Science (C4 2025-01) FRESH BLIND rust/Solana audit. Caught H-02 (migration_token_allocation
not persisted) + M-01 (last-buy wrong fee). Reasoning-gap misses reincorporated: M-02 (lamport invariant
includes rent) -> solana_account_model; M-03 (piecewise fee discontinuity) -> arithmetic. (H-01 lock_pool DoS
was a COVERAGE-gap miss, not reincorporated as a section.)"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_pump_science_miss_classes():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    for slug, fid in (("solana-lamport-invariant-includes-rent", "pump-science-2025-01-blind:M-02"),
                      ("fee-tier-boundary-discontinuity", "pump-science-2025-01-blind:M-03")):
        assert slug in c and c[slug]["status"] == "reincorporated"
        assert fid in c[slug]["awarded_examples"]
        assert "description" in c[slug] and "agent" in c[slug]


def test_pump_science_sections():
    sam = (ROOT / "agents" / "solana_account_model.md").read_text()
    assert "solana-lamport-invariant-includes-rent" in sam and "rent-exempt minimum" in sam and "lamports()" in sam
    ar = (ROOT / "agents" / "arithmetic.md").read_text()
    assert "fee-tier-boundary-discontinuity" in ar and "boundary" in ar.lower()
