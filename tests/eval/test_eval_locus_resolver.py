#!/usr/bin/env python3
"""Tests for the P194 eval-harness answer-key locus resolver (safe tiers + guardrails)."""
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "scripts").is_dir())
sys.path.insert(0, str(ROOT / "scripts"))
import eval_locus_resolver as r  # noqa: E402


def _idx(*fns):
    # fns: list of (contract, name)
    items = [{"kind": "function", "contract": c, "name": n, "id": f"function:{c}:{n}#x"} for c, n in fns]
    return r.build_manifest_index(items)


def test_direct_verbatim_from_title():
    idx = _idx(("V3Vault", "_cleanupLoan"), ("V3Vault", "borrow"))
    f = {"affected": "V3Vault", "title": "Reentrancy in _cleanupLoan before state update",
         "affected_functions": []}
    res = r.resolve_locus(f, idx)
    assert res["status"] == "RESOLVED" and res["function"] == "V3Vault._cleanupLoan"
    assert res["tier"] == "DIRECT_NAME_MISSED" and res["field_cited"] == "answer_key.title"


def test_alt_title_extraction():
    idx = _idx(("Market", "settleVaultsDebt"))
    f = {"affected": "Market", "title": "incorrect debt accounting",
         "alt_titles": ["bug in settleVaultsDebt rounding"]}
    res = r.resolve_locus(f, idx)
    assert res["status"] == "RESOLVED" and res["function"] == "Market.settleVaultsDebt"
    assert res["tier"] == "ALT_TITLE_MISSED"


def test_normalization_extraction():
    idx = _idx(("PanopticPool", "_forceExercise"))
    f = {"affected": "PanopticPool", "title": "issue", "affected_functions": ["forceExercise"]}
    res = r.resolve_locus(f, idx)
    assert res["status"] == "RESOLVED" and res["function"] == "PanopticPool._forceExercise"
    assert res["tier"] == "NORMALIZATION_FAILURE"


def test_generic_token_rejection():
    idx = _idx(("C", "transfer"), ("C", "balanceOf"))
    f = {"affected": "C", "title": "uses transfer and balanceOf and amount", "affected_functions": ["amount"]}
    res = r.resolve_locus(f, idx)
    # transfer/balanceOf are generic -> not auto-resolved
    assert res["status"] in ("UNRESOLVED", "REVIEW_GATED")
    assert res["function"] is None


def test_ambiguous_multi_match_no_autoselect():
    idx = _idx(("C", "redeemA"), ("C", "redeemB"))
    f = {"affected": "C", "title": "bug touches redeemA and redeemB"}
    res = r.resolve_locus(f, idx)
    assert res["status"] == "AMBIGUOUS" and res["function"] is None
    assert set(res["candidates"]) == {"redeemA", "redeemB"}


def test_contract_constrained_no_cross_contract():
    idx = _idx(("Other", "specialFunc"))
    f = {"affected": "Target", "title": "bug in specialFunc"}  # Target not in manifest
    res = r.resolve_locus(f, idx)
    assert res["status"] == "UNRESOLVED" and res["function"] is None


def test_no_broad_fuzzy_autoselect_getset_is_review_gated():
    idx = _idx(("Market", "getAutoDeleverageFactor"))
    f = {"affected": "Market", "title": "wrong value", "affected_functions": ["autoDeleverageFactor"]}
    res = r.resolve_locus(f, idx)
    # get-prefix drift must NOT auto-resolve
    assert res["status"] == "REVIEW_GATED" and res["tier"] == "GET_SET_DRIFT"
    assert res["function"] is None


def test_match_term_verbatim_only():
    idx = _idx(("VaultRouterBranch", "getVaultCreditCapacity"))
    f = {"affected": "VaultRouterBranch", "title": "credit capacity computed wrong"}
    res = r.resolve_locus(f, idx, match_terms=["getVaultCreditCapacity", "lockedCreditRatio"])
    assert res["status"] == "RESOLVED" and res["tier"] == "MATCH_TERM_MISSED"


def test_eval_harness_flags():
    assert r.EVAL_HARNESS_ONLY is True and r.ROUTES_IN_PRODUCTION is False


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
