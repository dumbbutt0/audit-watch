"""P107: evidence-free ranking prototype — RESEARCH-ONLY, un-wired.

Proves the prototype orders the already-enumerated surface by P106 signals, applies actor_clarity as a SOFT gate
(demote not drop), beats alphabetical on a constructed fixture, runs ablation, promotes/validates nothing, and is
deterministic. The live corpus run is exercised only when /tmp sources are present.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import rank_candidates_prototype as R  # noqa: E402

CORPUS = ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json"

_SRC = (
    "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.0;\n"
    "contract C {\n"
    "  mapping(address=>uint256) public bal; uint256 public total; address owner;\n"
    "  function withdrawAll() external { bal[msg.sender]+=1; total+=1; IERC20(t).transfer(msg.sender, total); }\n"
    "  function aaaPureView() external view returns (uint256) { return total; }\n"
    "  function bbbNoop() external view returns (uint256) { return total; }\n"
    "  function setOwner(address o) external { require(msg.sender==owner); owner=o; }\n"
    "}\n"
)


def _corpus(tmp_path):
    (tmp_path / "C.sol").write_text(_SRC, encoding="utf-8")
    return {
        "exclude_substrings": [],
        "subjects": [{
            "id": "fx", "phase": "test", "source_roots": [str(tmp_path)],
            "awarded_findings": [
                {"finding_id": "AWD", "contract": "C", "function": "withdrawAll",
                 "invariant_category": "per_user_accounting", "severity": "High",
                 "surfaceable": True, "grounding": "high"},
            ],
        }],
    }


def test_flags_unwired():
    assert R.FLAGS["is_gate"] is False
    assert R.FLAGS["research_only"] is True
    assert R.FLAGS["routes_in_production"] is False
    assert R.FLAGS["routed_manifest_ids"] == []


def test_self_test_passes():
    assert R._self_test() == 0


def test_defense_gap_and_category_excluded_from_all_variants():
    used = set()
    for feats in R.VARIANTS.values():
        used.update(feats)
    assert "defense_gap" not in used, "defense_gap must be excluded from pre-validation ranking (P106)"
    assert "category_specificity" not in used, "category_specificity must be excluded (P106 saturation)"
    assert R._GATE == "actor_clarity"  # gate-only, never a score feature
    assert "actor_clarity" not in used


def test_variant_beats_alphabetical_on_fixture(tmp_path):
    res = R.run_corpus(_corpus(tmp_path))
    base = res["variants"]["alphabetical_baseline"]["per_finding"][0]
    rec = res["variants"]["recommended"]["per_finding"][0]
    assert rec["rank"] < base["rank"], "recommended variant must rank the value-moving fn above alphabetical"


def test_soft_gate_demotes_but_does_not_drop(tmp_path):
    surfaces = R._surfaces(_corpus(tmp_path))
    ranked = R.rank_surface(surfaces["fx"]["surface"], R.VARIANTS["sharp_plus_moderate"])
    names = {r["function"] for r in ranked}
    assert "setOwner" in names, "role-guarded fn must remain in the ranked set (soft gate)"
    so = next(r for r in ranked if r["function"] == "setOwner")
    assert so["permissionless"] is False


def test_numeric_normalized_to_percentile_binary_to_unit():
    assert R._feature_norm("consequence_value_movement", 1.0, [0, 1]) == 1.0
    assert R._feature_norm("consequence_value_movement", 0.0, [0, 1]) == 0.0
    assert 0.0 <= R._feature_norm("state_write_breadth", 9.0, [0, 1, 9]) <= 1.0


def test_recommended_excludes_net_harmful(tmp_path):
    res = R.run_corpus(_corpus(tmp_path))
    nh = res["hard_stops"]["HS2_noise_over_signal"]["net_harmful_features"]
    rec = res["variants"]["recommended"]["features"]
    assert all(f not in rec for f in nh), "recommended variant must drop ablation-net-harmful features"


def test_ablation_present(tmp_path):
    res = R.run_corpus(_corpus(tmp_path))
    assert "per_feature" in res["ablation"]
    for feat in R.VARIANTS["sharp_plus_moderate"]:
        assert feat in res["ablation"]["per_feature"]
        assert "eligible" in res["ablation"]["per_feature"][feat]


def test_no_promotion_fields(tmp_path):
    res = R.run_corpus(_corpus(tmp_path))
    assert R.assert_no_promotion(res), "output must contain no validated/poc/report/submission/severity markers"


def test_deterministic(tmp_path):
    corpus = _corpus(tmp_path)
    a, b = R.run_corpus(corpus), R.run_corpus(corpus)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def _sources_present():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    return all(Path(r).exists() for s in corpus["subjects"] for r in s["source_roots"])


@pytest.mark.skipif(not _sources_present(), reason="burned /tmp subject sources not present")
def test_live_recommended_beats_baseline_and_no_promotion():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    res = R.run_corpus(corpus)
    assert R.assert_no_promotion(res)
    base = res["variants"]["alphabetical_baseline"]["metrics"]
    rec = res["variants"]["recommended"]["metrics"]
    assert (rec["top_3_recall"] > base["top_3_recall"]
            and rec["top_10_recall"] > base["top_10_recall"]
            and rec["median_rank"] < base["median_rank"]), "recommended must beat alphabetical on the pass criteria"
    # every awarded function is still locatable (ranking never drops a candidate)
    for s in res["variants"]["recommended"]["per_finding"]:
        assert s["found"] is True
