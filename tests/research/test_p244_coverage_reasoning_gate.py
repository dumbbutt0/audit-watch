"""P244 — coverage + reasoning-depth gate (SPEC/design-only). Read-only docs guard (no pipeline behavior)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p244_coverage_reasoning_gate"
SPEC = BASE / "COVERAGE_REASONING_GATE_SPEC.md"
REPLAY = BASE / "P241_MISS_REPLAY.md"
OPTIONS = BASE / "IMPLEMENTATION_OPTIONS.md"
VALIDATION = BASE / "VALIDATION_PLAN.md"
REC = BASE / "RECOMMENDATION.md"

VERDICTS = (
    "A — BUILD_COVERAGE_REASONING_GATE_NOW",
    "B — USE_AS_OPERATOR_CHECKLIST_ONLY",
    "C — NEED_MORE_ANALYSIS",
    "D — DO_NOT_BUILD",
)
# Part A read-states (the "examined-but-not-fully-read" honesty states the gate introduces)
READ_STATES = (
    "READ_FULL",
    "READ_PARTIAL",
    "NOT_IN_SCOPE",
    "GENERATED_INTERFACE_ONLY",
    "DUPLICATE_WRAPPER",
    "BLOCKED_BY_SIZE",
    "BLOCKED_BY_BUILD",
    "BLOCKED_BY_MISSING_SOURCE",
)
# Part E miss-replay labels
REPLAY_LABELS = (
    "recovered-by-coverage-gate",
    "recovered-by-lifecycle-matrix",
    "recovered-by-reasoning-checklist",
    "still-missed",
)


def test_all_deliverables_exist():
    for f in (SPEC, REPLAY, OPTIONS, VALIDATION, REC):
        assert f.exists(), f"missing P244 deliverable: {f.name}"


def test_recommendation_has_recognized_verdict():
    txt = REC.read_text()
    assert any(v in txt for v in VERDICTS), "no recognized P244 verdict token in RECOMMENDATION.md"


def test_spec_names_critical_item_rule_and_all_read_states():
    txt = SPEC.read_text()
    assert "critical" in txt.lower() and "READ_FULL" in txt, "Part A critical-item / READ_FULL rule missing"
    for s in READ_STATES:
        assert s in txt, f"read-state anchor missing from spec: {s}"


def test_replay_uses_all_four_labels_and_weighted_tally():
    txt = REPLAY.read_text()
    for lbl in REPLAY_LABELS:
        assert lbl in txt, f"miss-replay label missing: {lbl}"
    assert "Weighted" in txt or "weighted" in txt, "replay missing weighted tally"


def test_options_are_ranked_and_recommend_minimal_delta():
    txt = OPTIONS.read_text()
    # all five Part-F options must be present
    for kw in ("operator checklist", "dashboard", "CLI coverage gate", "rejection", "prompt wrapper"):
        assert kw.lower() in txt.lower(), f"implementation option missing: {kw}"
    assert "Recommended" in txt, "no recommended combination in IMPLEMENTATION_OPTIONS.md"


def test_research_only_no_production_edit_claim():
    # the spec must explicitly state it changes no production code this phase
    txt = SPEC.read_text().lower()
    assert "does not change any code" in txt or "design-only" in txt, "spec must state design-only / no-code-change"
