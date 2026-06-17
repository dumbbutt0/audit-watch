"""Phase-14b / Experiment E1b — semantic surface sampler + Candidate Coverage/Precision/provenance.

Covers: category name-regex capture (incl _blockAccount/getRewards/debtCeiling), min_score gating,
per-category cap bounding, candidate_queue.json shape + selected_by provenance, coverage-queue full union,
non-function exclusion, and the scorer's mechanical coverage/precision metrics. No LLM, no network.
"""
import importlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_context  # noqa: E402
prepare = importlib.import_module("deep_pass_prepare")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


SRC = "contract C {\n  function f() public { uint x = 1; }\n}\n"


def _item(mid, name, score=3, tags=None, inscope=True, kind="function"):
    return {"id": mid, "kind": kind, "name": name, "contract": "C", "file": "x.sol",
            "in_scope": inscope, "attack_surface_score": score, "tags": tags or [],
            "signature": f"function {name}()", "visibility": "public", "source_span": {"start_line": 2}}


def _manifest(ws, items):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"items": items}))


def _run(argv):
    old = sys.argv
    sys.argv = ["deep_pass_prepare"] + argv + ["--quiet", "--no-source"]
    try:
        return prepare.main()
    finally:
        sys.argv = old


# ───────────────────────── _categorize (pure) ─────────────────────────

def test_categorize_captures_the_missed_bugs():
    cats = prepare._load_surface_cats()
    assert "validator" in prepare._categorize("_blockAccount", set(), 2, cats)
    assert "reward" in prepare._categorize("getRewards", set(), 2, cats)
    assert "accounting" in prepare._categorize("debtCeiling", set(), 2, cats)


def test_e1d_new_vocab_categories_capture_oracle_and_trading():
    """Phase-15 e1d-v1: oracle/aggregator categories + trading_share terms in mint_redeem."""
    cats = prepare._load_surface_cats()
    assert "oracle" in cats and "aggregator" in cats        # new categories present (config-only)
    assert "oracle" in prepare._categorize("latestAnswer", set(), 2, cats)   # answer
    assert "oracle" in prepare._categorize("spot", set(), 2, cats)           # spot
    assert "aggregator" in prepare._categorize("MagicLpAggregator", set(), 3, cats)  # aggregat
    assert "mint_redeem" in prepare._categorize("buyShares", set(), 2, cats)  # buy + shares
    # min_score gating still holds on a new category (aggregator min_score 3)
    assert "aggregator" not in prepare._categorize("router", set(), 2, cats)
    assert "aggregator" in prepare._categorize("router", set(), 3, cats)


def test_categorize_min_score_gates():
    cats = prepare._load_surface_cats()
    # validator min_score is 2 → a score-1 validator name does not match
    assert prepare._categorize("validateThing", set(), 1, cats) == []
    assert "validator" in prepare._categorize("validateThing", set(), 2, cats)


def test_categorize_unrelated_name_empty():
    cats = prepare._load_surface_cats()
    assert prepare._categorize("foobarXyz", set(), 5, cats) == []


# ───────────────────────── prepare --surface-sample ─────────────────────────

def test_surface_sample_queue_has_provenance_and_categories(ws):
    _manifest(ws, [
        _item("function:C:getRewards", "getRewards", score=4),
        _item("function:C:foobar", "foobar", score=5),  # high score but no category → excluded
    ])
    _run(["--surface-sample"])
    q = json.loads((ws / "output" / "deep_pass" / "candidate_queue.json").read_text())
    names = {i["function"] for i in q["queue"]}
    assert "getRewards" in names and "foobar" not in names  # surface ∪ routed only, not raw high-surface
    gr = next(i for i in q["queue"] if i["function"] == "getRewards")
    assert "reward" in gr["categories"]
    assert "semantic_surface:reward" in gr["selected_by"]   # provenance recorded (change #3)


def test_surface_sample_per_category_cap_bounds(ws):
    # 20 reward-named fns; reward cap is 10 → bounded queue keeps ≤10 (by score)
    items = [_item(f"function:C:claim{i}", f"claim{i}", score=2 + (i % 5)) for i in range(20)]
    _manifest(ws, items)
    _run(["--surface-sample"])
    q = json.loads((ws / "output" / "deep_pass" / "candidate_queue.json").read_text())
    assert len(q["queue"]) <= 10  # capped


def test_coverage_queue_full_union_no_cap_no_bundles(ws):
    items = [_item(f"function:C:claim{i}", f"claim{i}", score=3) for i in range(20)]
    _manifest(ws, items)
    _run(["--coverage-queue"])
    q = json.loads((ws / "output" / "deep_pass" / "candidate_queue.json").read_text())
    assert q["mode"] == "coverage_queue" and len(q["queue"]) == 20  # no cap
    assert not list((ws / "output" / "deep_pass" / "_bundles").glob("dp_*.json"))  # no bundle bodies


def test_non_function_var_never_queued(ws):
    # creditMultiplier-style public state var (kind stateVariable) is not a function → never in queue
    _manifest(ws, [
        _item("var:C:creditMultiplier", "creditMultiplier", score=5, kind="stateVariable"),
        _item("function:C:getRewards", "getRewards", score=3),
    ])
    _run(["--surface-sample"])
    q = json.loads((ws / "output" / "deep_pass" / "candidate_queue.json").read_text())
    names = {i["function"] for i in q["queue"]}
    assert "creditMultiplier" not in names and "getRewards" in names


# ───────────────────────── scorer: mechanical coverage/precision ─────────────────────────

def _scorer():
    spec = importlib.util.spec_from_file_location(
        "score_generalization",
        ROOT / "documentation" / "evals" / "promotion_benchmark" / "score_generalization.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


