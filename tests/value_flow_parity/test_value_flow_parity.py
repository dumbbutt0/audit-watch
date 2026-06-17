"""Tests for the value_flow_parity research lens (deterministic, no LLM, no network)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import value_flow_parity_taxonomy as vfp  # noqa: E402
import value_flow_parity_audit as audit  # noqa: E402
import sibling_function_parity_taxonomy as sfp  # noqa: E402
import audit_context  # noqa: E402


def _pairfeat(name, snippet, calls=None):
    return {"name": name, "guard_idents": vfp.guard_idents(snippet),
            "effect_operands": vfp.effect_operands(snippet),
            "calls_lower": set(c.lower() for c in (calls or []))}


# ---------- CATCH (shape 2 — the M-02 anchor) ----------

def test_m02_threshold_value_mismatch_medium():
    """Size M-02: a raw `amount` checked against a CREDIT-named threshold => medium."""
    body = ("function validateSellCreditMarket(State storage state, P params) external view {"
            " if (params.amount < state.riskConfig.minimumCreditBorrowAToken) revert MinCredit(); }")
    cands = vfp.classify_intra("validateSellCreditMarket", "", body)
    m = [c for c in cands if c["shape"] == "threshold_value_mismatch"]
    assert m and m[0]["confidence"] == "medium" and m[0]["guard_value"] == "amount", cands


def test_validate_execute_value_mismatch_medium():
    val = _pairfeat("validateSellCreditMarket",
                    "if (params.amount < minimumCreditBorrowAToken) revert M();")
    exe = _pairfeat("executeSellCreditMarket",
                    "creditAmountIn = computeCredit(params.amount); state.book(creditAmountIn);",
                    calls=["computeCredit", "book"])
    # ensure derived appears as an operand/call
    exe["effect_operands"].add("creditamountin")
    cands = vfp.classify_validate_execute_pair(val, exe)
    assert any(c["shape"] == "validate_execute_value_mismatch" and c["confidence"] == "medium"
               for c in cands), cands


def test_net_gross_low():
    body = "function f() returns (uint256 x){ x = gross; token.transfer(to, x - fees); return x; }"
    cands = vfp.classify_intra("f", "", body)
    assert any(c["shape"] == "net_gross_mismatch" and c["confidence"] == "low" for c in cands), cands


# ---------- HARMLESS / FP controls ----------

def test_identity_divergence_is_low_not_routable():
    """checking msg.sender then transferring to recipient is the NORMAL pattern -> never high/medium."""
    body = ("function transfer(address recipient, uint256 amount) external {"
            " require(msg.sender != address(0)); erc20.transfer(recipient, amount); }")
    cands = vfp.classify_intra("transfer", "", body)
    assert all(c["confidence"] == "low" for c in cands if c["shape"] == "identity_check_vs_use")
    assert not any(c["confidence"] in ("high", "medium") for c in cands)


def test_plain_amount_check_not_flagged():
    body = "function validateX(uint256 amount) { require(amount > 0, 'zero'); }"
    cands = vfp.classify_intra("validateX", "", body)
    assert [c for c in cands if c["confidence"] in ("high", "medium")] == []


def test_asset_source_family_not_value_flow_scope():
    """A pure asset-source-family transfer mismatch (asset_source_consistency territory) is NOT flagged."""
    body = ("function pay(uint256 amount) { require(amount > 0);"
            " collateralSource.transfer(supplyReceiver, amount); }")
    cands = vfp.classify_intra("pay", "", body)
    assert [c for c in cands if c["confidence"] in ("high", "medium")] == []


def test_threshold_with_matching_basis_not_flagged():
    """amount checked against an amount-named bound (no credit/derived keyword) -> no candidate."""
    body = "function validateX(uint256 amount) { if (amount < minimumAmount) revert(); }"
    cands = vfp.classify_intra("validateX", "", body)
    assert [c for c in cands if c["shape"] == "threshold_value_mismatch"] == []


# ---------- end-to-end (research-only contract) ----------

def test_audit_research_only_flags_and_anchor(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    import sibling_function_parity_audit as sfa
    monkeypatch.setattr(sfa, "ROOT", tmp_path)
    src = ("contract SellCreditMarket {\n"
           "function validateSellCreditMarket(State storage state, P params) external view {\n"
           "  if (params.amount < state.riskConfig.minimumCreditBorrowAToken) revert MinCredit();\n"
           "}\n}\n")
    (tmp_path / "SellCreditMarket.sol").write_text(src)
    items = [{"id": "function:SellCreditMarket:validateSellCreditMarket#a", "kind": "function",
              "contract": "SellCreditMarket", "name": "validateSellCreditMarket",
              "file": "SellCreditMarket.sol",
              "signature": "function validateSellCreditMarket(State storage state, P params) external view",
              "visibility": "external", "mutability": "view", "modifiers": [], "in_scope": True,
              "source_span": {"start_line": 2, "end_line": 4}}]
    man = tmp_path / "coverage_manifest.json"
    man.write_text(json.dumps({"items": items}))
    monkeypatch.setattr(sys, "argv", ["x", "--manifest", str(man), "--quiet"])
    audit.main()
    rep = json.loads((tmp_path / "output" / "value_flow_parity_audit.json").read_text())
    assert rep["is_gate"] is False and rep["research_only"] is True
    assert rep["routes_in_production"] is False and rep["routed_manifest_ids"] == []
    assert any(c["shape"] == "threshold_value_mismatch" and c["confidence"] == "medium"
               for c in rep["candidates"]), rep["candidates"]
