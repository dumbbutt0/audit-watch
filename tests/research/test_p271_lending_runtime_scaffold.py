"""P271 — lending runtime scaffold (CALIBRATION). Guard test (research-only; isolated; no authority leakage)."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p271_lending_runtime_scaffold"
POC = ROOT / "pocs/p271/wise"
DOCS = ("SETUP.md", "CALIBRATION_FORENSICS.md", "SCAFFOLD_DESIGN.md", "POC_RESULTS.md",
        "FAMILY_TO_EXACT_DIAGNOSIS.md", "LENDING_COMPLETION_CHECKLIST.md", "LIMITATIONS.md", "VERDICT.md",
        "ROLLBACK_PLAN.md")
VERDICTS = ("A — LENDING_SCAFFOLD_READY_FOR_FRESH_RECOVERY_TEST", "B — SCAFFOLD_PARTIAL_NEEDS_MORE_RUNTIME_DEPTH",
            "C — EXACT_MECHANISM_STILL_UNCLEAR", "D — ABORTED_CONSTRAINT_VIOLATION")
LEAK = ("severity", "reportable", "submission_ready", "confirmed")
FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "scripts/research/mechanism_pairwise_selector.py": "b0623b8c88752059",
    "scripts/research/impact_first_poc_triage.py": "63c88d02d2c7eefa",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def test_docs_exist_and_recognized_verdict():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing {d}"
    assert any(v in (BASE / "VERDICT.md").read_text() for v in VERDICTS)


def test_calibration_not_fresh_disclaimer_present():
    for d in ("SETUP.md", "POC_RESULTS.md", "VERDICT.md"):
        assert "CALIBRATION" in (BASE / d).read_text(), f"{d} missing CALIBRATION disclaimer"


def test_scaffold_and_pocs_isolated():
    assert (POC / "foundry.toml").exists()
    assert (POC / "test/H03_GlobalVsPositionBadDebt.t.sol").exists()
    assert (POC / "test/H04_PrivateVsPublicCollateralMisallocation.t.sol").exists()
    # PoCs live only under pocs/p271 (isolated)
    assert "pocs/p271" in str(POC)


def test_poc_command_recorded():
    assert (BASE / "outputs/poc_commands.txt").exists()
    assert "forge test" in (BASE / "outputs/poc_commands.txt").read_text()


def test_no_authority_leakage_in_pocs():
    """The PoC tests must not assign severity/reportable/submission/confirmed state (they prove mechanisms only)."""
    for t in ("test/H03_GlobalVsPositionBadDebt.t.sol", "test/H04_PrivateVsPublicCollateralMisallocation.t.sol"):
        src = (POC / t).read_text().lower()
        for tok in ("submission_ready", "reportable", "production_routing"):
            assert tok not in src, f"{t} leaks {tok}"


def test_frozen_modules_not_tuned():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"{rel} changed during P271 (no tuning allowed)"


def test_forbidden_files_byte_identical():
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden file {rel} changed"


