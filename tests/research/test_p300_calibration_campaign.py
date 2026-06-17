"""P300 — multi-target calibration campaign: recall + novelty + executed-PoC validity + submission filter + GO bands.

Runs `forge` (validity is by real execution). Answer keys + contest source + ground_truth + promoted rules READ-ONLY.
"""
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/research"))
import executed_poc_verifier as epv  # noqa: E402
import submission_filter as sf  # noqa: E402
import shutil

D = ROOT / "documentation/research/assisted_mode/p300_calibration_campaign"
O = D / "outputs"
FORGE = shutil.which("forge")
needs_forge = pytest.mark.skipif(FORGE is None, reason="forge not installed")

VERIFIER_HASH = "1a005811fbb9e0d0"
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
READ_ONLY = {
    "data/fp_autopsies/rejection_rules.jsonl": "a9f393935ab349d5",
    "audits/silo-finance-2025-03-strict-eval/output/eval_ready/match_matrix.json": "e5f8ac1e4b1f7971",
    "audits/revert-lend-2024-03-strict-eval/output/eval_ready/match_matrix.json": "13e26496d4e10f81",
    "audits/panoptic-2025-12-strict-eval/output/eval_ready/match_matrix.json": "33eaf5e29118dea0",
}
DOC_FILES = ("DESIGN.md", "CAMPAIGN_RESULTS.md", "EVIDENCE_AUDIT.md", "REAL_HUNT_READINESS.md", "LIMITATIONS.md",
             "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — ", "B — ", "C — ", "D — ")


def _sc():
    return json.loads((O / "campaign_scorecard.json").read_text())


# ---- recall + novelty axes ----
def test_per_target_recall_and_novelty():
    pt = _sc()["per_target"]
    assert pt["silo-finance-2025-03-strict-eval"]["recall"]["recall_useful"] == 0.5
    for t, e in pt.items():
        assert 0.0 <= e["recall"]["recall_useful"] <= 1.0
        assert e["novelty"]["n"] >= 0 and "novel" in e["novelty"]


# ---- validity + FP=0 ----
def test_confirmed_fp_zero_corpus_wide():
    assert _sc()["aggregate"]["confirmed_false_positive_count"] == 0
    assert _sc()["aggregate"]["submission_filter"]["filter_leaks"] == 0


def test_range_confirmations_across_targets():
    agg = _sc()["aggregate"]
    assert agg["targets_with_a_confirmation"] >= 2  # range across multiple targets


@needs_forge
@pytest.mark.parametrize("slug,fid", [("silo", "M-05"), ("silo", "M-06"), ("panoptic", "M-01")])
def test_logic_confirmations_verifier_backed(slug, fid):
    r = epv.verify_poc(ROOT / "pocs/p300" / f"{slug}__{fid}", finding_id=f"{slug}-{fid}")
    assert r["validity_confirmed"] is True and r["status"] == "confirmed_by_logic_differential"


@needs_forge
def test_refuted_locus_not_confirmed():
    r = epv.verify_poc(ROOT / "pocs/p300/revert__H-03", finding_id="revert-H-03")
    assert r["validity_confirmed"] is False  # honest refute (per-token approval gates the claimed impact)


# ---- submission filter (the precision lever) ----
def test_submission_filter_semantics():
    assert sf.filter_record({"validity_confirmed": True, "status": "confirmed_by_execution", "attacker_verified": True})["label"] == "submit"
    assert sf.filter_record({"validity_confirmed": True, "status": "confirmed_by_logic_differential"})["label"] == "submit"
    assert sf.filter_record({"validity_confirmed": False, "status": "setup_only"})["label"] == "needs_human"
    # fabricated: validity flag set but no real confirmed status -> needs_human (filter trusts the verdict)
    assert sf.filter_record({"validity_confirmed": True, "status": "inconclusive"})["label"] == "needs_human"


def test_submission_filter_results_no_leak():
    f = json.loads((O / "submission_filter_results.json").read_text())
    assert f["filter_leaks"] == 0
    assert f["submit"] == len(f["submit_loci"])


# ---- staged proposals (human-promote later); promoted artifacts unchanged ----
def test_proposals_staged_not_promoted():
    p = ROOT / "data/learning/_proposed/p300_rejection_rule_proposals.jsonl"
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    assert len(rows) >= 1 and all(r["promoted"] is False for r in rows)
    assert all(r["status"] == "PROPOSED_HUMAN_PROMOTE_REQUIRED" for r in rows)


def test_ground_truth_not_referenced_for_write():
    for s in ("eval_campaign.py", "submission_filter.py"):
        t = (ROOT / "scripts/research" / s).read_text()
        assert "ground_truth" not in t and "promote_learning" not in t


# ---- authority / integrity ----
def test_verifier_and_forbidden_byte_identical():
    assert hashlib.sha256((ROOT / "scripts/research/executed_poc_verifier.py").read_bytes()).hexdigest()[:16] == VERIFIER_HASH
    for rel, h in FORBIDDEN.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:8].startswith(h), f"forbidden changed: {rel}"


def test_unwired_from_confirm_gates():
    for rel in ("scripts/confirm_gate.py", "scripts/min_confirm_gate.py"):
        txt = (ROOT / rel).read_text()
        assert "eval_campaign" not in txt and "submission_filter" not in txt


def test_no_leakage_advisory_stamps():
    for name in ("campaign_scorecard.json", "submission_filter_results.json"):
        r = json.loads((O / name).read_text())
        for fld in ("reportable", "submission_ready", "concluded", "auto_submitted"):
            if fld in r:
                assert r[fld] is False
        if "severity" in r:
            assert r["severity"] is None


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    assert any(v in (D / "VERDICT.md").read_text() for v in VERDICTS)


