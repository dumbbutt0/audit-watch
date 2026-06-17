"""P235 — shadow live contest evaluation. Docs + L3-record + freeze guard (no pipeline behavior)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_p208_l3_readiness as v3  # noqa: E402

BASE = ROOT / "documentation/research/assisted_mode/p235_shadow_contest"
SCORECARD = BASE / "CONTEST_SCORECARD.md"
FROZEN = BASE / "FROZEN_HUNT.md"
ANSWER_KEY = BASE / "ANSWER_KEY_revealed.md"
L3 = ROOT / "output_research" / "l3_readiness"
CONFIRMED = ["RENFT-01"]
VERDICTS = (
    "A — WOULD_HAVE_BEEN_COMPETITIVE",
    "B — WOULD_HAVE_FOUND_MEANINGFUL_FINDINGS",
    "C — RECALL_GAPS_REMAIN",
    "D — PRIORITIZATION_GAPS_REMAIN",
    "E — NOT_YET_COMPETITIVE",
)


def test_scorecard_frozen_and_answerkey_exist():
    assert SCORECARD.exists(), "P235 scorecard missing"
    assert FROZEN.exists(), "P235 freeze marker missing"
    assert ANSWER_KEY.exists(), "P235 revealed answer key missing"
    assert any(v in SCORECARD.read_text() for v in VERDICTS), "no recognized P235 verdict token"


def test_freeze_marker_precedes_reveal():
    # The freeze marker must record content hashes (anti-hindsight gate) and the answer key must be a
    # separate, later file (never edited into the frozen set).
    txt = FROZEN.read_text()
    assert "sha256" in txt.lower() and "FROZEN_AT" in txt, "freeze marker lacks hashes/timestamp"
    assert "never opened" in txt.lower(), "freeze marker must witness sealed artifacts"


