"""P232 — multi-architecture scaffold design & validation: docs + scaffold-artifact guard.

Asserts the report exists with a valid build verdict, the dependency map exists, and the reference scaffold
primitives + ported harness are present. Touches no pipeline behavior.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p232_scaffold"
REPORT = BASE / "SCAFFOLD_DESIGN_VALIDATION.md"
DEPMAP = BASE / "DEPENDENCY_MAP.md"

SCAFFOLD = [
    ROOT / "pocs/lib/HarnessBase.sol",
    ROOT / "pocs/lib/MutableIndexPool.sol",
    ROOT / "pocs/p232/primitives/test/Primitives.t.sol",
    ROOT / "pocs/p232/decent/test/DEC01_scaffolded.t.sol",
]
VERDICTS = ("A — BUILD_NOW", "B — DESIGN_MORE", "C — LOW_PRIORITY")


def test_report_exists_with_verdict():
    assert REPORT.exists(), "P232 scaffold report missing"
    text = REPORT.read_text()
    assert any(v in text for v in VERDICTS), "no recognized build verdict token"


def test_dependency_map_exists():
    assert DEPMAP.exists(), "P232 dependency map missing"


def test_reference_scaffold_artifacts_exist():
    for p in SCAFFOLD:
        assert p.exists(), f"missing scaffold artifact: {p}"


def test_success_criteria_section_present():
    text = REPORT.read_text()
    assert "Success-criteria check" in text and "All 5 pass" in text
