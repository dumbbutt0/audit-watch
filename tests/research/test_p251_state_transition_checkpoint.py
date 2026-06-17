"""P251 — state-transition examine-time checkpoint. Docs guard (no pipeline behavior)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p251_state_transition_checkpoint"
DOCS = ("ARCHITECTURE.md", "IMPLEMENTATION.md", "REPLAY.md", "FP_REVIEW.md", "RECOMMENDATION.md")
VERDICTS = ("A — READY_FOR_DEFAULT_OFF_USE", "B — NEEDS_TUNING", "C — ARCHITECTURE_DOES_NOT_HELP")


def test_all_docs_exist():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing P251 doc: {d}"


def test_recommendation_recognized_verdict():
    assert any(v in (BASE / "RECOMMENDATION.md").read_text() for v in VERDICTS)


def test_replay_five_anchors_before_after():
    txt = (BASE / "REPLAY.md").read_text()
    for m in ("munchables H-01", "kleidi M-01", "munchables M-01", "decent H-04", "kleidi M-03"):
        assert m in txt, f"replay missing anchor {m}"
    assert "5/5 candidates" in txt and "5/5 chains" in txt


def test_no_emit_invariant_in_architecture():
    arch = (BASE / "ARCHITECTURE.md").read_text()
    assert "emits findings" in arch.lower() and "never" in arch.lower()


def test_outputs_are_reasoning_records_zero_conclusions():
    outs = list((BASE / "outputs").glob("*_stcheckpoint.json"))
    assert outs, "no replay output JSONs"
    for f in outs:
        d = json.loads(f.read_text())
        assert d["emits_findings"] is False and d["concludes_vulnerability"] is False
        assert d["output_type"] == "reasoning_records"
        assert all(r.get("severity") is None and r.get("concluded") is False for r in d["records"])
