"""P263 — fresh scored recall-first proof. Guard: no-tuning, freeze integrity, scored verdict, isolation."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p263_fresh_scored_recall_proof"
OUTS = BASE / "outputs"
DOCS = ("TARGET_SCREEN.md", "SETUP.md", "BASE_FREEZE.md", "PRIORITIZER_OUTPUT.md", "RECALL_SWEEP.md",
        "SELECTED_LOCI.md", "RANKING_OUTPUTS.md", "PROCEDURE_OUTPUTS.md", "REVEAL_AND_SCORE.md",
        "P263_DIAGNOSIS.md", "VERDICT.md")
VERDICTS = ("A — RECALL_FIRST_PROMOTED", "B — RECALL_FIRST_PROMISING_NEEDS_MORE",
            "C — RECALL_FIRST_DID_NOT_IMPROVE_RECALL", "D — ABORTED_CONTAMINATION_OR_CONSTRAINT")
# Frozen module/config hashes (P263 must not tune them).
FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "config/research_locus_shape_prioritizer.json": "c61da091ad3ed21e",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "config/research_recall_first_shape_sweep.json": "62e860199e7c51cd",
}


def _sha16(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()[:16]


def test_all_docs_exist_and_verdict():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing {d}"
    assert any(v in (BASE / "VERDICT.md").read_text() for v in VERDICTS)


def test_modules_not_tuned():
    for path, h in FROZEN.items():
        assert _sha16(path) == h, f"{path} changed during P263 proof (tuning forbidden)"


def test_freeze_hashes_echoed_in_reveal():
    rev = (BASE / "REVEAL_AND_SCORE.md").read_text()
    for h in ("b7e8b0fc", "29459529", "12e67226", "aea8d04f"):
        assert h in rev, f"freeze hash {h} missing in reveal"


def test_recall_delta_recorded():
    sw = (BASE / "RECALL_SWEEP.md").read_text()
    assert "RECALL-DELTA" in sw or "recall delta" in sw.lower()
    rev = (BASE / "REVEAL_AND_SCORE.md").read_text()
    assert "FORCED_BY_RECALL_SWEEP" in rev
    assert "narrow" in rev.lower()  # baseline comparison present


def test_sweep_output_advisory_and_bounded():
    d = json.loads((OUTS / "benddao_recall_sweep.json").read_text())
    assert d["emits_findings"] is False and d["concludes_vulnerability"] is False
    assert len(d["swept_loci"]) <= 25
    for s in d["swept_loci"]:
        for m in s["candidate_mechanisms"]:
            assert m.get("severity") is None and m.get("concluded") is False


def test_isolation_target_not_in_audits():
    assert not (ROOT / "audits/2024-07-benddao").exists()
    assert not (ROOT / "audits/benddao").exists()
    for f in ("benddao_coverage_manifest.json", "benddao_accounting_checkpoint.json",
              "benddao_prioritizer.json", "benddao_recall_sweep.json"):
        assert (OUTS / f).exists(), f"missing isolated output {f}"
