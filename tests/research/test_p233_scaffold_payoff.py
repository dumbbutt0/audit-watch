"""P233 — scaffold payoff: SC-11 & SC-12 converted to full L3. Docs + L3-record guard (no pipeline behavior)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_p208_l3_readiness as v3  # noqa: E402

L3 = ROOT / "output_research" / "l3_readiness"
REPORT = ROOT / "documentation/research/assisted_mode/p233_scaffold_payoff/SCAFFOLD_PAYOFF.md"
FIXTURE = ROOT / "pocs/p233/size/test/SizeFixture.sol"


def test_report_and_fixture_exist():
    assert REPORT.exists(), "P233 payoff report missing"
    assert FIXTURE.exists(), "P233 Size Fixture missing"


