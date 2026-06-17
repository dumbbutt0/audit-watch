"""P240 — second shadow contest with advisory lenses. Docs + freeze guard (no pipeline behavior)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p240_second_shadow_contest"
SCORECARD = BASE / "CONTEST_SCORECARD.md"
FROZEN = BASE / "FROZEN_HUNT.md"
ANSWER_KEY = BASE / "ANSWER_KEY_revealed.md"
OUTPUTS = BASE / "outputs"

VERDICTS = (
    "A — ADVISORY_LENSES_PROVEN",
    "B — PROMISING_BUT_NEED_MORE_SHADOWS",
    "C — NO_RECALL_LIFT",
    "D — TOO_NOISY",
    "E — BASE_RECALL_STILL_TOO_LOW",
)


def test_scorecard_frozen_and_answerkey_exist():
    assert SCORECARD.exists() and FROZEN.exists() and ANSWER_KEY.exists()
    assert any(v in SCORECARD.read_text() for v in VERDICTS), "no recognized P240 verdict token"


def test_freeze_marker_precedes_reveal():
    txt = FROZEN.read_text()
    assert "sha256" in txt.lower() and "FROZEN_AT" in txt
    assert "never opened" in txt.lower()


def test_advisory_lens_outputs_are_research_only_and_unrouted():
    for name in ("pooltogether_safe.json", "pooltogether_hostile.json"):
        rep = json.loads((OUTPUTS / name).read_text())
        assert rep.get("research_only") is True
        assert rep.get("routes_in_production") is False
        assert rep.get("routed_manifest_ids") == []
        assert rep.get("is_gate") is False
