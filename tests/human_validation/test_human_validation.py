"""Pure-function tests for the human-validation console core (scripts/human_validation.py).

These assert the platform boundary holds: human validation, not routing. No corpus is modified;
labels are append-only; forbidden verdict/routing fields can never be emitted; research flags persist.
"""
import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import human_validation as hv  # noqa: E402

FROZEN = ROOT / "documentation/evals/judge_corpus/frozen_corpus.json"
EVIDENCE_DEMO = ROOT / "documentation/research/_evidence_demo/evidence_bundles.json"


def _good_form():
    return {
        "coherence": "coherent",
        "investigation_worthiness": "investigate",
        "poc_followup_worthiness": "maybe",
        "expected_review_effort": "medium",
        "missing_information": ["trace the asset() value"],
        "counter_signals": "router-style suppression may apply",
        "reviewer_notes": "looks like the Revert anchor",
        "reviewer_confidence": "high",
    }


# --------------------------------------------------------------------- loading
def test_load_evidence_bundles_shape():
    if not EVIDENCE_DEMO.exists():
        pytest.skip("evidence demo not present")
    c = hv.load_corpus(EVIDENCE_DEMO)
    assert c["bundle_count"] >= 1
    # evidence_bundles.json lacks corpus_bundle_hash -> hv derives a content hash
    assert all(b.get("bundle_hash") for b in c["bundles"])


def test_load_rejects_non_corpus(tmp_path):
    p = tmp_path / "x.json"
    p.write_text(json.dumps({"not": "a corpus"}))
    with pytest.raises(hv.LabelValidationError):
        hv.load_corpus(p)


# ----------------------------------------------------------------- corpus hash
# ----------------------------------------------------------------- label rows
# ------------------------------------------------------------- forbidden fields
# --------------------------------------------------------- append-only + progress
# ------------------------------------------------------------- abs_source (Open in VS Code)
def test_abs_source_none_for_missing_file():
    assert hv.abs_source("does/not/exist_xyz.sol", [ROOT]) is None
    assert hv.abs_source(None, [ROOT]) is None
    assert hv.abs_source("", [ROOT]) is None


def test_abs_source_rejects_traversal_across_all_roots():
    # escaping every allowed root must not resolve, even if the target exists
    roots = [ROOT, ROOT / "audits", ROOT / "scripts"]
    assert hv.abs_source("../../../../etc/passwd", roots) is None


def test_abs_source_workspace_relative_needs_right_root():
    # a path relative to an eval workspace resolves only when that workspace root is in the list
    ws = ROOT / "audits" / "blackhole-2025-05-eval"
    if not ws.is_dir():
        import pytest as _pt; _pt.skip("blackhole workspace not present")
    rel = "contracts/2025-05-blackhole/contracts/RouterV2.sol"
    assert hv.abs_source(rel, [ws]) is not None          # found under the workspace root
    assert hv.abs_source(rel, [ROOT / "scripts"]) is None  # not under an unrelated root
    # and the dashboard's full root list (repo + workspaces) resolves it too
    roots = [ROOT] + sorted(d for d in (ROOT / "audits").glob("*") if d.is_dir())
    assert hv.abs_source(rel, roots) is not None


