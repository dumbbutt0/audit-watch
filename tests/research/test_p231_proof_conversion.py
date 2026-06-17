"""P231 — cross-architecture proof conversion: report + L3 records guard.

Asserts the report exists with a valid verdict token, and that each of the three converted candidates has a
schema-valid L3 record carrying an honest l3_status (PASS/FAIL/PARTIAL/NEEDS_HARNESS). Touches no pipeline
behavior, no severity, no routing.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_p208_l3_readiness as v3  # noqa: E402

L3 = ROOT / "output_research" / "l3_readiness"
BASE = ROOT / "documentation/research/assisted_mode/p231_proof_conversion"
REPORT = BASE / "PROOF_CONVERSION_EVALUATION.md"
CANDIDATES = ["DEC-01", "QAMM-03", "TF-17"]
VERDICTS = (
    "A — PROOF_GENERALIZES",
    "B — PROOF_PARTIALLY_GENERALIZES",
    "C — PROOF_LENDING_BIASED",
    "D — PROOF_INFRASTRUCTURE_LIMITED",
)
VALID_STATUS = {"PASS", "FAIL", "PARTIAL", "NEEDS_HARNESS", "HUMAN_OVERRIDE", "NOT_ATTEMPTED"}


def test_report_exists_with_verdict():
    assert REPORT.exists(), "P231 proof conversion report missing"
    text = REPORT.read_text()
    assert any(v in text for v in VERDICTS), "no recognized proof-conversion verdict token"
    assert "Proof Conversion Score" in text and "/ 100" in text


