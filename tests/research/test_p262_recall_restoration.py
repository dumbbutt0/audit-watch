"""P262 — one-shot recall restoration with zero-conclusion-FP guard. Guard + behavior tests (research-only)."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/research/recall_first_shape_sweep.py"
CFG = ROOT / "config/research_recall_first_shape_sweep.json"
PROMPT = ROOT / "prompts/research/recall_first_shape_sweep.md"
DOCS = ROOT / "documentation/research/assisted_mode/p262_recall_restoration"
OUTS = DOCS / "outputs"
P260_MODULE = ROOT / "scripts/research/locus_shape_prioritizer.py"
P260_CFG = ROOT / "config/research_locus_shape_prioritizer.json"
DOC_FILES = ("SETUP.md", "RECALL_REGRESSION_DIAGNOSIS.md", "MODULE_SPEC.md", "IMPLEMENTATION_NOTES.md",
             "BACKTEST_RESULTS.md", "FP_GUARD.md", "LIMITATIONS.md", "VERDICT.md")
VERDICTS = ("A — RECALL_FIX_READY_FOR_FRESH_PROOF", "B — RECALL_FIX_PROMISING_NEEDS_REFINEMENT",
            "C — RECALL_FIX_NOT_USEFUL", "D — BUILD_ABORTED_CONSTRAINT_VIOLATION")
STATUS = ("RECALL_CANDIDATE_ONLY", "NEEDS_RANKING", "NEEDS_COMPLETION", "NEEDS_REFUTATION")
BT_LABELS = ("FORCED_INTO_SWEEP", "RIGHT_TEMPLATE", "AWARD_SHAPE_GENERATED", "WOULD_REACH_BC_RANKING",
             "STILL_MISSED", "INCONCLUSIVE")
TEMPLATES = tuple(f"T{i}" for i in range(1, 10))
FORBIDDEN = ("severity", "concluded", "vulnerability", "reportable", "submission_ready")
# P260 baseline (must stay unchanged — recall sweep reuses, never modifies it)
P260_MODULE_SHA16 = "d6b494bc3c0cc746"
P260_CFG_SHA16 = "c61da091ad3ed21e"


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def test_files_and_docs_exist():
    assert SCRIPT.exists() and CFG.exists() and PROMPT.exists()
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)


def test_p260_reused_not_modified():
    assert _sha16(P260_MODULE) == P260_MODULE_SHA16, "P260 module changed (must be reused, not modified)"
    assert _sha16(P260_CFG) == P260_CFG_SHA16, "P260 config changed"


def test_config_caps_and_t9_lower_priority():
    c = json.loads(CFG.read_text())
    assert c["is_gate"] is False and c["research_only"] is True and c["routes_in_production"] is False
    caps = c["caps"]
    assert caps["max_swept_loci_json"] == 25 and caps["max_mechs_per_locus"] == 5 and caps["max_total_mechs_to_ranking"] == 30
    assert c["t9_math_units"]["rank_last"] is True  # T9 optional/lower-priority
    # recall-first name policy includes checkpoint-hit high-risk functions
    for kw in ("deposit", "withdraw", "liquidate", "rebalance", "harvest", "redeem"):
        assert kw in c["recall_first"]["name_keywords"]


def test_outputs_bounded_and_no_conclusions():
    outs = list(OUTS.glob("*_recall_sweep.json"))
    assert len(outs) >= 3
    for f in outs:
        d = json.loads(f.read_text())
        assert d["emits_findings"] is False and d["concludes_vulnerability"] is False
        assert len(d["swept_loci"]) <= 25
        assert d["total_mechs_to_ranking"] <= 30
        for s in d["swept_loci"]:
            assert s["status_label"] in STATUS
            assert len(s["candidate_mechanisms"]) <= 5
            for m in s["candidate_mechanisms"]:
                assert m.get("severity") is None
                for fld in FORBIDDEN:
                    assert m.get(fld) in (None, False), f"forbidden field {fld} set"


def test_t9_recovers_basin_math_loci():
    d = json.loads((OUTS / "basin_recall_sweep.json").read_text())
    math = {s["function"] for s in d["swept_loci"] if s["t9_applied"]}
    assert "decodeWellData" in math or any("calc" in m.lower() for m in math), "T9 did not recover basin math loci"


def test_skipped_award_locus_forced_in():
    """The headline: the P259-skipped hybra GrowthHYBR.deposit is forced into the sweep."""
    d = json.loads((OUTS / "hybra_recall_sweep.json").read_text())
    assert any(s["function"].lower() == "deposit" for s in d["swept_loci"])


def test_backtest_doc_has_classification_labels():
    bt = (DOCS / "BACKTEST_RESULTS.md").read_text()
    assert "FORCED_INTO_SWEEP" in bt
    assert any(l in bt for l in ("RIGHT_TEMPLATE", "AWARD_SHAPE_GENERATED", "WOULD_REACH_BC_RANKING"))


