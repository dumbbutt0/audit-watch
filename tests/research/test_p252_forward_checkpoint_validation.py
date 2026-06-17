"""P252 — forward checkpoint validation (controlled A/B). Docs guard (no pipeline behavior)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p252_forward_checkpoint_validation"
DOCS = ("SETUP.md", "BASELINE_RUN.md", "CHECKPOINT_RUN.md", "REVEAL_AND_SCORE.md",
        "CONTRIBUTION_ANALYSIS.md", "METRICS.md", "VERDICT.md")
VERDICTS = ("A — CHECKPOINTS_PRODUCE_REAL_RECALL_LIFT", "B — ARCHITECTURE_VALIDATED_BUT_LIFT_UNPROVEN",
            "C — NO_MEASURABLE_VALUE", "D — BURDEN_EXCEEDS_BENEFIT")
CONTRIB_LABELS = ("BASE_ONLY", "CHECKPOINT_ONLY", "BASE_PLUS_CHECKPOINT", "MISSED")


def test_all_docs_exist():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing P252 doc: {d}"


def test_verdict_recognized():
    assert any(v in (BASE / "VERDICT.md").read_text() for v in VERDICTS)


def test_contribution_table_has_all_four_labels():
    txt = (BASE / "CONTRIBUTION_ANALYSIS.md").read_text()
    for l in CONTRIB_LABELS:
        assert l in txt, f"contribution label missing: {l}"


def test_freeze_before_reveal_hashes():
    cp = (BASE / "CHECKPOINT_RUN.md").read_text()
    assert "Arm A freeze hash" in cp
    rev = (BASE / "REVEAL_AND_SCORE.md").read_text()
    assert "AFTER both freezes" in rev


def test_checkpoint_outputs_zero_conclusions():
    outs = list((BASE / "outputs").glob("*_checkpoint.json"))
    assert len(outs) >= 2, "expected both checkpoint outputs"
    for f in outs:
        d = json.loads(f.read_text())
        assert d["emits_findings"] is False and d["concludes_vulnerability"] is False
        assert all(r.get("severity") is None and r.get("concluded") is False for r in d["records"])
