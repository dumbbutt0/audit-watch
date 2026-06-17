"""P5 — Solana PoC template (litesvm, L3 standard) + ZK boundary doc."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_solana_poc_template_has_three_layers():
    lib = (ROOT / "templates" / "solana_poc" / "src" / "lib.rs").read_text()
    assert "l1_entry_unprivileged" in lib
    assert "l2_state_flip" in lib
    assert "l3_outcome" in lib
    assert "litesvm" in lib.lower()
    cargo = (ROOT / "templates" / "solana_poc" / "Cargo.toml").read_text()
    assert "litesvm" in cargo and "solana-sdk" in cargo


def test_solana_poc_readme():
    r = (ROOT / "templates" / "solana_poc" / "README.md").read_text()
    assert "L1" in r and "L2" in r and "L3" in r and "Level 3" in r


def test_zk_boundary_doc():
    d = (ROOT / "documentation" / "architecture" / "zk_boundary.md").read_text()
    for kw in ("ElGamal", "BitVM", "FLAG", "zk_out_of_scope", "never adjudicate"):
        assert kw in d, kw
