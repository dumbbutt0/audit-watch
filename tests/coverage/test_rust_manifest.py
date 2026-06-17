"""Rust/Solana coverage-manifest extraction. Locks: pub fn -> external high-surface item; Solana taxonomy
tags (signer/cpi/account_validation/pda/accounting) drive the value-at-risk score; const captured; the Solidity
taxonomy + scoring is untouched (ACTIVE_TAG_KEYWORDS swap is local to a rust run).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_coverage_manifest as bcm  # noqa: E402

SAMPLE = """use anchor_lang::prelude::*;
#[program]
pub mod vault {
    pub fn withdraw(ctx: Context<Withdraw>, amount: u64) -> Result<()> { Ok(()) }
    fn internal_helper(x: u64) -> u64 { x + 1 }
}
const SEED_PREFIX: &[u8] = b"vault";
"""


def test_rust_tag_keywords_solana_concepts():
    # the Solana taxonomy must define the value-at-risk tags the score rewards
    for t in ("permissions", "account_validation", "cpi", "pda", "accounting"):
        assert t in bcm.RUST_TAG_KEYWORDS
    assert "signer" in bcm.RUST_TAG_KEYWORDS["permissions"]
    assert "invoke_signed" in bcm.RUST_TAG_KEYWORDS["cpi"]
    assert "find_program_address" in bcm.RUST_TAG_KEYWORDS["pda"]


def test_rust_manifest_end_to_end(tmp_path):
    src = tmp_path / "src"; src.mkdir()
    (src / "lib.rs").write_text(SAMPLE)
    out = tmp_path / "m.json"
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_coverage_manifest.py"),
                        "--contract", str(src), "--out", str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    items = json.loads(out.read_text())["items"]
    by = {i["name"]: i for i in items}
    assert "withdraw" in by and by["withdraw"]["visibility"] == "external"
    assert by["withdraw"]["attack_surface_score"] >= 3          # pub handler ranks high
    assert by["internal_helper"]["visibility"] == "internal"
    assert by["internal_helper"]["attack_surface_score"] < by["withdraw"]["attack_surface_score"]
    assert "SEED_PREFIX" in by and by["SEED_PREFIX"]["kind"] == "constant"


def test_solidity_taxonomy_still_default():
    # module default taxonomy is Solidity (a rust run swaps ACTIVE locally); guard against leakage
    assert bcm.ACTIVE_TAG_KEYWORDS is bcm.TAG_KEYWORDS or "amm_pol" in bcm.ACTIVE_TAG_KEYWORDS
    assert "amm_pol" in bcm.TAG_KEYWORDS and "signer" not in bcm.TAG_KEYWORDS.get("permissions", ())
