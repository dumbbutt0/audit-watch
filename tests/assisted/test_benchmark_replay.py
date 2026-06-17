"""P105: reproducibility benchmark (surfacing layer) — RESEARCH-ONLY, un-wired.

Proves the benchmark harness drives the FROZEN run_subject/inventory pipeline (no copies), scores awarded findings
mechanically (function_enumerated / invariant generated / category match), excludes unsurfaceable findings from
denominators, promotes nothing in a recall-only run (false_promotions=0), and is deterministic. The corpus on disk
is consistency-checked; the live cross-subject run is exercised only when the burned /tmp sources are present.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import benchmark_replay as B  # noqa: E402

CORPUS = ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json"


# ----------------------------------------------------------------- fixtures

def _fixture_corpus(tmp_path):
    """A hermetic 1-subject corpus: one HIT (public fn), one MISS (absent fn), one INTERNAL, one UNSURFACEABLE."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "Hit.sol").write_text(
        "pragma solidity ^0.8.0;\ncontract Hit {\n"
        "  uint256 public total; mapping(address=>uint256) public balance;\n"
        "  function withdraw(uint256 amount) external { balance[msg.sender]-=amount; total-=amount; }\n"
        "  function _helper() internal { total++; }\n}\n", encoding="utf-8")
    return {
        "exclude_substrings": ["/test"],
        "caveats": ["fixture"],
        "subjects": [{
            "id": "fx", "contest": "fx", "phase": "test", "source_roots": [str(src)],
            "benchmark_findings_are_subset": True,
            "awarded_findings": [
                {"finding_id": "HIT", "contract": "Hit", "function": "withdraw",
                 "invariant_category": "per_user_accounting", "severity": "High",
                 "surfaceable": True, "surfaceable_reason": "public", "grounding": "high",
                 "conversion": {"validated": True, "poc_attempted": True, "poc_succeeded": True, "evidence_ref": "fx"}},
                {"finding_id": "MISS", "contract": "Hit", "function": "ghost",
                 "invariant_category": "value_conservation", "severity": "Medium",
                 "surfaceable": True, "surfaceable_reason": "public", "grounding": "high"},
                {"finding_id": "INTERNAL", "contract": "Hit", "function": "_helper",
                 "invariant_category": "value_conservation", "severity": "Low",
                 "surfaceable": True, "surfaceable_reason": "n/a", "grounding": "inferred"},
                {"finding_id": "UNSURF", "contract": "Hit", "function": None,
                 "invariant_category": "value_conservation", "severity": "High",
                 "surfaceable": False, "surfaceable_reason": "missing-function class", "grounding": "high"},
            ],
        }],
    }


# ----------------------------------------------------------------- unit tests

def test_flags_unwired():
    assert B.FLAGS["is_gate"] is False
    assert B.FLAGS["research_only"] is True
    assert B.FLAGS["routes_in_production"] is False
    assert B.FLAGS["routed_manifest_ids"] == []


def test_rate_matches_compute_metrics_contract():
    assert B._rate(0, 0)["value"] is None
    assert B._rate(0, 0)["n"] == 0
    assert B._rate(1, 2) == {"value": 0.5, "n": 2, "numerator": 1}


def test_self_test_passes():
    assert B._self_test() == 0


def test_public_function_is_scored_as_hit(tmp_path):
    res = B.run_corpus(_fixture_corpus(tmp_path))
    rows = {r["finding_id"]: r for r in res["subjects"][0]["scored_findings"]}
    assert rows["HIT"]["function_enumerated"] is True
    assert rows["HIT"]["relevant_invariant_generated"] is True
    assert rows["HIT"]["category_invariant_generated"] is True


def test_absent_and_internal_functions_are_not_enumerated(tmp_path):
    res = B.run_corpus(_fixture_corpus(tmp_path))
    rows = {r["finding_id"]: r for r in res["subjects"][0]["scored_findings"]}
    assert rows["MISS"]["function_enumerated"] is False, "a function not in source must not score as covered"
    assert rows["INTERNAL"]["function_enumerated"] is False, "internal functions are not public/external surface"


def test_unsurfaceable_excluded_from_denominator(tmp_path):
    res = B.run_corpus(_fixture_corpus(tmp_path))
    s0 = res["subjects"][0]
    assert len(s0["scored_findings"]) == 3
    assert len(s0["unsurfaceable_findings"]) == 1
    assert res["aggregate"]["enumeration_coverage_rate_all"]["n"] == 3


def test_recall_only_run_promotes_nothing(tmp_path):
    res = B.run_corpus(_fixture_corpus(tmp_path))
    assert res["aggregate"]["false_promotions_total"] == 0
    assert all(not s["false_promotions"] for s in res["subjects"])


def test_conversion_counted_only_with_evidence(tmp_path):
    res = B.run_corpus(_fixture_corpus(tmp_path))
    agg = res["aggregate"]
    assert agg["poc_attempted"] == 1 and agg["poc_succeeded"] == 1
    rows = {r["finding_id"]: r for r in res["subjects"][0]["scored_findings"]}
    assert rows["MISS"]["relevant_candidate_validated"] == B.NOT_ATTEMPTED
    assert rows["MISS"]["poc_succeeded"] == B.NOT_ATTEMPTED


def test_deterministic(tmp_path):
    corpus = _fixture_corpus(tmp_path)
    a, b = B.run_corpus(corpus), B.run_corpus(corpus)
    def strip(r):
        c = json.loads(json.dumps(r))
        for s in c["subjects"]:
            s["runtime_ms"] = 0
        return c
    assert json.dumps(strip(a), sort_keys=True) == json.dumps(strip(b), sort_keys=True)


# ----------------------------------------------------------------- corpus consistency

def test_corpus_is_well_formed():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    assert corpus["is_gate"] is False and corpus["routes_in_production"] is False
    assert corpus["caveats"], "corpus must carry the retrospective-ceiling caveats"
    ids = set()
    for s in corpus["subjects"]:
        assert s["source_roots"], f"{s['id']} needs source_roots"
        for f in s["awarded_findings"]:
            assert f["finding_id"] not in ids, f"duplicate finding id {f['finding_id']}"
            ids.add(f["finding_id"])
            assert f["invariant_category"]
            assert isinstance(f["surfaceable"], bool)
            if f["surfaceable"]:
                assert f["function"], f"{f['finding_id']} surfaceable but has no function"


# ----------------------------------------------------------------- live integration (guarded)

def _corpus_sources_present():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    return all(Path(r).exists() for s in corpus["subjects"] for r in s["source_roots"])


@pytest.mark.skipif(not _corpus_sources_present(), reason="burned /tmp subject sources not present")
def test_live_corpus_run_preserves_precision():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    res = B.run_corpus(corpus)
    agg = res["aggregate"]
    assert agg["false_promotions_total"] == 0, "recall-only run must promote nothing"
    assert agg["grounded_findings_scored"] > 0
    # every awarded function we mapped must be a real public/external entrypoint (catches stale corpus)
    for s in res["subjects"]:
        for r in s["scored_findings"]:
            assert r["function_enumerated"] is True, f"{r['finding_id']} no longer enumerates — corpus drifted"
