"""P261 — fresh heldout proof of the P260 prioritizer. Docs guard + no-tuning + isolation checks."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p261_fresh_prioritizer_proof"
OUTS = BASE / "outputs"
MODULE = ROOT / "scripts/research/locus_shape_prioritizer.py"
MODULE_CFG = ROOT / "config/research_locus_shape_prioritizer.json"
DOCS = ("TARGET_SCREEN.md", "SETUP.md", "BASE_FREEZE.md", "PRIORITIZER_OUTPUT.md", "SELECTED_LOCI.md",
        "RANKING_OUTPUTS.md", "PROCEDURE_OUTPUTS.md", "REVEAL_AND_SCORE.md", "P261_DIAGNOSIS.md", "VERDICT.md")
BOTTLENECKS = ("TARGET_FIT_GAP", "P260_LOCUS_PRIORITIZATION_GAP", "SHAPE_GENERATION_GAP", "PROFILE_BC_RANKING_GAP",
               "COMPLETION_GAP", "PROCEDURE_WORKING", "INCONCLUSIVE_CORPUS_LIMIT")
VERDICTS = ("PROMOTE_P260_TO_NEXT_HARNESS_STAGE", "REFINE_P260_PRIORITIZER", "BUILD_RANKING_LAYER_NEXT",
            "RETURN_TO_DISCOVERY_RESEARCH", "NEEDS_MORE_FRESH_HELDOUT", "STOP_NOT_USEFUL",
            "ABORTED_CONTAMINATION_OR_CONSTRAINT")
# Frozen P260 module hashes recorded at the start of P261 (proves no tuning during the proof).
P260_MODULE_SHA16 = "d6b494bc3c0cc746"
P260_CFG_SHA16 = "c61da091ad3ed21e"


def _sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def test_all_docs_exist():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing {d}"


def test_bottleneck_and_verdict_recognized():
    v = (BASE / "VERDICT.md").read_text()
    assert any(b in v for b in BOTTLENECKS) and any(x in v for x in VERDICTS)


def test_p260_module_not_tuned_during_proof():
    """The proof must not modify the module under test."""
    assert _sha16(MODULE) == P260_MODULE_SHA16, "locus_shape_prioritizer.py changed during P261 (tuning forbidden)"
    assert _sha16(MODULE_CFG) == P260_CFG_SHA16, "prioritizer config changed during P261 (tuning forbidden)"


def test_reveal_unavailable_is_honest():
    rev = (BASE / "REVEAL_AND_SCORE.md").read_text()
    assert "REVEAL UNAVAILABLE" in rev or "not public" in rev
    assert "0 awarded issues scored" in rev or "cannot" in rev.lower()
    # freeze hashes echoed for deferred reveal
    for h in ("949e0f2f6e803ad7", "fc5901a39c6f91fa", "a65b8b876cd97e44"):
        assert h in rev, f"freeze hash {h} missing in reveal doc"


def test_prioritizer_output_research_only_and_bounded():
    d = json.loads((OUTS / "monetrix_prioritizer.json").read_text())
    assert d["is_gate"] is False and d["research_only"] is True and d["routes_in_production"] is False
    assert d["emits_findings"] is False and d["concludes_vulnerability"] is False
    assert len(d["prioritized_loci"]) <= d["top_n"]
    for lc in d["prioritized_loci"]:
        for m in lc["generated_mechanism_hypotheses"]:
            assert m["severity"] is None and m["concluded"] is False


def test_fresh_source_isolated_not_committed():
    """Cloned monetrix source must NOT be under the repo audits/ or committed paths."""
    assert not (ROOT / "audits/2026-04-monetrix").exists()
    assert not (ROOT / "audits/monetrix").exists()
    # checkpoint outputs for the fresh run present (used by the prioritizer)
    assert (OUTS / "monetrix_accounting_checkpoint.json").exists()
    assert (OUTS / "monetrix_state_transition_checkpoint.json").exists()
    assert (OUTS / "monetrix_coverage_manifest.json").exists()
