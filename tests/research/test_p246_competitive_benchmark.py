"""P246 — competitive readiness benchmark. Read-only docs/freeze guard (no pipeline behavior)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p246_competitive_benchmark"
CONTESTS = ("decent-2024-01-holdout", "vultisig-2024-06-holdout", "kleidi-2024-10-holdout",
            "centrifuge-2023-09-holdout", "munchables-2024-05-holdout", "badger-2024-06-holdout")
VERDICTS = ("A — COMPETITIVE", "B — LIVE_HUNT_READY", "C — ASSISTED_HUNTER", "D — RESEARCH_SYSTEM")
SCORE_CLASSES = ("DIRECT_HIT", "PARTIAL_HIT", "SAME_ROOT_CAUSE", "SAME_AREA_WRONG_MECHANISM", "MISSED")
MISS_BUCKETS = ("Coverage", "Reasoning depth", "Oracle freshness", "Reward/emission",
                "Economic invariant", "EIP4626", "Permit/signature", "Reentrancy", "Cross-chain",
                "Governance", "Unknown")


def test_core_deliverables_exist():
    for f in ("BENCHMARK_PLAN.md", "CONTEST_SELECTION.md", "AGGREGATE_RESULTS.md",
              "MISS_ATTRIBUTION.md", "READINESS_ASSESSMENT.md"):
        assert (BASE / f).exists(), f"missing P246 deliverable: {f}"


def test_six_contest_scorecards_and_frozen_candidates():
    for c in CONTESTS:
        assert (BASE / "per_contest" / c / "FROZEN_CANDIDATES.md").exists(), f"{c}: no frozen candidates"
        assert (BASE / "per_contest" / c / "SCORECARD.md").exists(), f"{c}: no scorecard"


def test_freeze_before_reveal_discipline():
    # every scorecard must record a freeze hash before reveal
    for c in CONTESTS:
        txt = (BASE / "per_contest" / c / "SCORECARD.md").read_text()
        assert "Freeze hash:" in txt and "before reveal" in txt, f"{c}: freeze-before-reveal not asserted"


def test_readiness_has_recognized_verdict():
    txt = (BASE / "READINESS_ASSESSMENT.md").read_text()
    assert any(v in txt for v in VERDICTS), "no recognized P246 readiness verdict"


def test_scoring_taxonomy_present():
    agg = (BASE / "AGGREGATE_RESULTS.md").read_text()
    assert "weighted recall" in agg.lower()
    miss = (BASE / "MISS_ATTRIBUTION.md").read_text()
    for b in ("Coverage", "Reasoning depth", "Cross-chain"):
        assert b in miss, f"miss bucket missing: {b}"
