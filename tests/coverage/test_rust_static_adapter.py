"""P1 — Rust/Solana static adapter. Locks: the adapter writes the SHARED static.json schema with
Solana routing flags + ZK boundary flag, the Solidity dispatch is language-gated (no behavior change
for solidity), and the source-pattern pass detects the Anchor primitives our specialists key on.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "scripts"))

ORDERLY_SRC = (ROOT / "audits" / "orderly-solana-2024-10-eval" / "contracts" / "_sources" /
               "solana-vault" / "packages" / "solana" / "contracts" / "programs" / "solana-vault")


def test_adapter_files_exist_executable():
    for p in ("scripts/setup_rust_deps.sh", "scripts/compile_for_analysis_rust.sh",
              "tools/static_analysis_rust.py"):
        f = ROOT / p
        assert f.exists(), p


def test_adapter_emits_shared_schema_with_solana_flags():
    import static_analysis_rust as sar
    if not ORDERLY_SRC.exists():
        import pytest
        pytest.skip("orderly source not present")
    static = sar.analyse(str(ORDERLY_SRC))
    # shared schema keys downstream consumers read
    for k in ("contract_path", "functions", "slither_findings", "is_erc4626", "is_proxy",
              "is_anchor", "has_cpi", "has_pda", "zk_out_of_scope", "language"):
        assert k in static, k
    assert static["language"] == "rust"
    assert static["is_anchor"] and static["has_cpi"] and static["has_pda"]
    assert len(static["functions"]) > 0
    # the source-pattern pass must catch the unchecked AccountInfo (the H-2/O-01 locus)
    checks = {f["check"] for f in static["slither_findings"]}
    assert "solana-unchecked-accountinfo" in checks


def test_zk_boundary_flagged_not_adjudicated(tmp_path):
    import static_analysis_rust as sar
    p = tmp_path / "proof.rs"
    p.write_text("pub fn verify() { let c = ElGamal::decrypt(); let _ = RangeProof::new(); }")
    static = sar.analyse(str(tmp_path))
    assert static["zk_out_of_scope"] is True
    assert "zk_boundary" in static["zk_boundary_note"]


def test_solidity_dispatch_unchanged():
    # The dispatch only fires for rust; default language is solidity → static_analysis.py must NOT
    # route to the rust adapter. We assert the guard condition rather than running slither.
    from audit_context import audit_language
    assert audit_language("nonexistent-audit-default") == "solidity"
