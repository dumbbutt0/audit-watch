"""P241 — final frozen-system benchmark. Docs + freeze guard (no pipeline behavior)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p241_final_benchmark"
AGG = BASE / "AGGREGATE_BENCHMARK.md"
FROZEN = BASE / "FROZEN.md"
PC = BASE / "per_contest"

VERDICTS = (
    "A — TOP_TIER_COMPETITIVE",
    "B — COMPETITIVE",
    "C — FINDINGS_BUT_MISSES_MAJOR_AWARDS",
    "D — NOT_YET_COMPETITIVE",
)
RECS = (
    "Proceed to supervised live hunting",
    "Build one additional detector family",
    "Build one additional reasoning family",
    "Improve ranking",
    "Improve proof conversion",
)


def test_aggregate_and_freeze_exist():
    assert AGG.exists() and FROZEN.exists()
    txt = AGG.read_text()
    assert any(v in txt for v in VERDICTS), "no recognized P241 verdict token"
    assert any(r in txt for r in RECS), "no recognized recommendation token"


def test_freeze_marker_precedes_reveal():
    txt = FROZEN.read_text()
    assert "sha256" in txt.lower() and "FROZEN_AT" in txt
    assert "never opened" in txt.lower()


def test_at_least_three_contests_scored():
    scorecards = list(PC.glob("*/SCORECARD.md"))
    assert len(scorecards) >= 3, f"need >=3 per-contest scorecards, found {len(scorecards)}"


def test_advisory_lens_outputs_research_only():
    for f in PC.glob("*/outputs/*_safe.json"):
        rep = json.loads(f.read_text())
        assert rep.get("research_only") is True and rep.get("routed_manifest_ids") == []
    for f in PC.glob("*/outputs/*_hostile.json"):
        rep = json.loads(f.read_text())
        assert rep.get("research_only") is True and rep.get("routed_manifest_ids") == []
