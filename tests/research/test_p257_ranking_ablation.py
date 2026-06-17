"""P257 — subtle mechanism ranking confirmation + ablation. Docs guard (no pipeline behavior)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p257_ranking_ablation"
TOP_DOCS = ("SETUP.md", "RANKING_DIAGNOSIS.md", "VERDICT.md")
# notional = fully scored; reserve = excluded (precheck-contaminated) -> only base+reveal docs required
NOTIONAL_DOCS = ("notional_BASE_FREEZE.md", "notional_SELECTED_LOCI.md", "notional_MECHANISM_ENUM.md",
                 "notional_RANKING_ABLATION.md", "notional_PROCEDURE_OUTPUTS.md", "notional_REVEAL_AND_SCORE.md")
RESERVE_DOCS = ("reserve_BASE_FREEZE.md", "reserve_REVEAL_AND_SCORE.md")
VERDICTS = ("A — RANKING_HARNESS_BUILD_READY", "B — RANKING_PROMISING_NEEDS_MORE_HELDOUT",
            "C — DISCOVERY_GAP_DOMINATES", "D — COMPLETION_GAP_DOMINATES",
            "E — RANKING_PROFILES_NOT_USEFUL", "F — STOP_NOT_USEFUL")
OPS = ("STATE_TRANSITION_SIMULATION", "ADVERSARIAL_ACTOR_SUBSTITUTION", "TERMINAL_STATE_EVALUATION",
       "INVARIANT_DELTA_COMPUTATION", "CROSS_CALL_IDENTITY_TRACKING")
PROFILES = ("Profile A", "Profile B", "Profile C")
AWARDED_CLASSES = ("NOT_ENUMERATED", "ENUMERATED_BUT_RANKED_TOO_LOW",
                   "RANKED_HIGH_BUT_NOT_COMPLETED", "COMPLETED_CORRECTLY")
PROFILE_LABELS = ("SELECTED_AWARDED", "TOP2_AWARDED", "MISRANKED_AWARDED", "MISSED")


def test_all_docs_exist():
    for d in TOP_DOCS + NOTIONAL_DOCS + RESERVE_DOCS:
        assert (BASE / d).exists(), f"missing doc {d}"


def test_verdict_recognized():
    assert any(v in (BASE / "VERDICT.md").read_text() for v in VERDICTS)


def test_reveal_availability_precheck_in_setup():
    setup = (BASE / "SETUP.md").read_text()
    assert "REVEAL_AVAILABILITY_PRECHECK" in setup
    assert "reserve" in setup.lower() and "contaminat" in setup.lower()


def test_five_ops_named_in_setup():
    setup = (BASE / "SETUP.md").read_text()
    for op in OPS:
        assert op in setup, f"op {op} not in SETUP.md"


def test_three_profiles_present_in_ablation():
    abl = (BASE / "notional_RANKING_ABLATION.md").read_text()
    for p in PROFILES:
        assert p in abl, f"{p} missing in ablation"


def test_four_awarded_classes_and_profile_labels_present():
    diag = (BASE / "RANKING_DIAGNOSIS.md").read_text()
    rev = (BASE / "notional_REVEAL_AND_SCORE.md").read_text()
    for c in AWARDED_CLASSES:
        assert c in diag or c in rev, f"awarded class missing: {c}"
    for lbl in PROFILE_LABELS:
        assert lbl in rev, f"profile label missing in reveal: {lbl}"


def test_freeze_hashes_echoed_in_notional_reveal():
    rev = (BASE / "notional_REVEAL_AND_SCORE.md").read_text()
    for h in ("7f6ce9fe9c88ca18", "377e7ed87703c5bc", "4fe67b745d31581d",
              "93535debae9cdbe4", "6328a06659ab025c"):
        assert h in rev, f"freeze hash {h} missing in notional reveal"


def test_checkpoint_outputs_zero_conclusions():
    outs = list((BASE / "outputs").glob("*_checkpoint.json"))
    assert len(outs) >= 4, "expected 2 checkpoints x 2 contests"
    for f in outs:
        d = json.loads(f.read_text())
        assert d["emits_findings"] is False and d["concludes_vulnerability"] is False
        assert all(r.get("severity") is None and r.get("concluded") is False for r in d["records"])
