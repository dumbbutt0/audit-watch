"""P249 — accounting examine-time checkpoint. Docs guard (no pipeline behavior)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p249_accounting_checkpoint"
DOCS = ("ARCHITECTURE.md", "IMPLEMENTATION.md", "REPLAY.md", "FP_REVIEW.md", "RECOMMENDATION.md")
VERDICTS = ("A — READY_FOR_DEFAULT_OFF_USE", "B — NEEDS_TUNING", "C — ARCHITECTURE_DOES_NOT_HELP")


def test_all_docs_exist():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing P249 doc: {d}"


def test_recommendation_recognized_verdict():
    assert any(v in (BASE / "RECOMMENDATION.md").read_text() for v in VERDICTS)


def test_replay_has_five_misses_and_before_after():
    txt = (BASE / "REPLAY.md").read_text()
    for m in ("kleidi M-02", "centrifuge M-05", "centrifuge M-07", "munchables M-03", "munchables M-04"):
        assert m in txt, f"replay missing {m}"
    assert "5/5 candidates" in txt and "5/5 chains" in txt


def test_no_emit_invariant_asserted_in_docs():
    arch = (BASE / "ARCHITECTURE.md").read_text()
    assert "emits_findings" in arch and "never" in arch.lower()


def test_replay_outputs_are_reasoning_records_not_findings():
    outs = list((BASE / "outputs").glob("*_checkpoint.json"))
    assert outs, "no replay output JSONs"
    for f in outs:
        d = json.loads(f.read_text())
        assert d["emits_findings"] is False and d["concludes_vulnerability"] is False
        assert d["output_type"] == "reasoning_records"
        assert all(r.get("severity") is None and r.get("concluded") is False for r in d["records"])
