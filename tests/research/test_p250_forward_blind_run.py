"""P250 — forward blind run (accounting checkpoint, unseen target). Docs guard (no pipeline behavior)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p250_forward_blind_run"
DOCS = ("SETUP.md", "BASE_HUNT_FROZEN.md", "CHECKPOINT_PASS.md", "REVEAL_AND_SCORE.md", "METRICS.md",
        "RECOMMENDATION.md")
VERDICTS = ("A — CONFIRMED_GENERALIZES", "B — PARTIAL_GENERALIZATION", "C — DOES_NOT_GENERALIZE")
METRICS = ("Accounting candidates born", "exploit chains", "Question volume", "Time overhead",
           "Recall lift", "FP / noise")


def test_all_docs_exist():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing P250 doc: {d}"


def test_verdict_recognized():
    assert any(v in (BASE / "RECOMMENDATION.md").read_text() for v in VERDICTS)


def test_freeze_before_reveal_hashes_present():
    rev = (BASE / "REVEAL_AND_SCORE.md").read_text()
    assert "freeze" in rev.lower() and "AFTER both freezes" in rev
    cp = (BASE / "CHECKPOINT_PASS.md").read_text()
    assert "Base freeze hash" in cp


def test_six_metrics_present():
    txt = (BASE / "METRICS.md").read_text()
    for m in METRICS:
        assert m in txt, f"missing metric: {m}"


def test_checkpoint_output_is_reasoning_records_zero_findings():
    f = BASE / "outputs" / "spectra_checkpoint.json"
    assert f.exists(), "missing spectra checkpoint output"
    d = json.loads(f.read_text())
    assert d["emits_findings"] is False and d["concludes_vulnerability"] is False
    assert all(r.get("severity") is None and r.get("concluded") is False for r in d["records"])
