"""P234 — targeted precision gate. Docs + L3-record guard (no pipeline behavior)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_p208_l3_readiness as v3  # noqa: E402

BASE = ROOT / "documentation/research/assisted_mode/p234_precision_gate"
REPORT = BASE / "PRECISION_GATE.md"
FROZEN = BASE / "FROZEN_CANDIDATES.md"
L3 = ROOT / "output_research" / "l3_readiness"
CONFIRMED = ["LAMBO-01", "DYAD-03", "DYAD-01"]
VERDICTS = (
    "A — LIVE_HUNT_READY",
    "B — LIVE_HUNT_READY_WITH_LIMITS",
    "C — NEED_ONE_MORE_PRECISION_GATE",
    "D — NOT_READY_PRECISION",
)


def test_report_and_frozen_exist():
    assert REPORT.exists(), "P234 precision gate report missing"
    assert FROZEN.exists(), "P234 frozen candidate set missing"
    assert any(v in REPORT.read_text() for v in VERDICTS), "no recognized precision-gate verdict token"


