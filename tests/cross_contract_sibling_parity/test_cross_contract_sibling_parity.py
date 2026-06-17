"""Tests for the cross_contract_sibling_parity research lens (deterministic, no LLM, no network)."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import cross_contract_sibling_parity_taxonomy as ccs  # noqa: E402
import cross_contract_sibling_parity_audit as audit  # noqa: E402
import audit_context  # noqa: E402

DIR = "contracts/libraries/actions"


def _f(name, contract, snippet="", sig=None, modifiers=None, visibility="external", file=None):
    sig = sig if sig is not None else f"function {name}(State storage state, P calldata params) external view"
    file = file if file is not None else f"{DIR}/{contract}.sol"
    feat = ccs.extract_cross_features(name, sig, modifiers, snippet, visibility=visibility,
                                      file=file, contract=contract)
    feat["own_calls"] = feat["calls"]
    feat["own_ncalls"] = feat["_ncalls"]
    return feat


# ---------- CATCH ----------

def test_anchor_size_m06_forsale_high():
    strong = _f("validateBuyCreditMarket", "BuyCreditMarket",
                "state.getCreditPosition(id); state.getDebtPosition(id); "
                "if (user.allCreditPositionsForSaleDisabled || !creditPosition.forSale) revert NotForSale();")
    weak = _f("validateSellCreditMarket", "SellCreditMarket",
              "state.getCreditPosition(id); state.getDebtPosition(id); if (tenor > max) revert Range();")
    cands = ccs.classify_cross_pair(strong, weak)
    assert any(c["parity_type"] == "validation_parity" and "forsale" in c["missing_component"]
               and c["confidence"] == "high" and c["weak_contract"] == "SellCreditMarket"
               for c in cands), cands


# ---------- HARMLESS / gates ----------

def test_no_shared_object_suffix_suppressed():
    """validateBuyCreditMarket vs validateClaim share verb+state-struct but NOT the object (CreditMarket)."""
    strong = _f("validateBuyCreditMarket", "BuyCreditMarket",
                "state.getCreditPosition(id); if (!creditPosition.forSale) revert NF();")
    weak = _f("validateClaim", "Claim", "state.getCreditPosition(id); state.getDebtPosition(id);")
    assert ccs.classify_cross_pair(strong, weak) == []


def test_different_module_dir_suppressed():
    strong = _f("validateBuyMarket", "BuyMarket",
                "state.getCreditPosition(id); if(!creditPosition.forSale) revert NF();",
                file="contracts/a/BuyMarket.sol")
    weak = _f("validateSellMarket", "SellMarket", "state.getCreditPosition(id); state.x();",
              file="contracts/b/SellMarket.sol")
    assert ccs.classify_cross_pair(strong, weak) == []


def test_different_state_struct_suppressed():
    strong = _f("validateBuyMarket", "BuyMarket",
                "state.getCreditPosition(id); if(!creditPosition.forSale) revert NF();",
                sig="function validateBuyMarket(StateA storage state, P p) external")
    weak = _f("validateSellMarket", "SellMarket", "s.getCreditPosition(id); s.x();",
              sig="function validateSellMarket(StateB storage s, P p) external")
    assert ccs.classify_cross_pair(strong, weak) == []


def test_too_few_shared_calls_suppressed():
    strong = _f("validateBuyMarket", "BuyMarket", "onlyThis(); if(!x.forSale) revert NF();")
    weak = _f("validateSellMarket", "SellMarket", "differentCall(); otherThing();")
    assert ccs.classify_cross_pair(strong, weak) == []


def test_both_admin_suppressed():
    strong = _f("validateBuyMarket", "BuyMarket",
                "state.getCreditPosition(id); state.y(); if(!x.forSale) revert NF();", modifiers=["onlyOwner"])
    weak = _f("validateSellMarket", "SellMarket", "state.getCreditPosition(id); state.y();",
              modifiers=["onlyOwner"])
    assert ccs.classify_cross_pair(strong, weak) == []


def test_weak_internal_suppressed():
    strong = _f("validateBuyMarket", "BuyMarket",
                "state.getCreditPosition(id); state.y(); if(!x.forSale) revert NF();")
    weak = _f("validateSellMarket", "SellMarket", "state.getCreditPosition(id); state.y();",
              visibility="internal")
    cands = ccs.classify_cross_pair(strong, weak)
    assert all(c["weak_contract"] != "SellMarket" for c in cands)


def test_weak_already_guards_field_not_flagged():
    strong = _f("validateBuyMarket", "BuyMarket",
                "state.getCreditPosition(id); state.y(); if(!cp.forSale) revert NF();")
    weak = _f("validateSellMarket", "SellMarket",
              "state.getCreditPosition(id); state.y(); if(!cp.forSale) revert NF();")
    assert [c for c in ccs.classify_cross_pair(strong, weak) if "forsale" in c["missing_component"]] == []


# ---------- end-to-end (research-only contract) ----------

def _write_manifest(tmp_path):
    buy = ("function validateBuyCreditMarket(State storage state, P calldata params) external view {"
           " state.getCreditPosition(id); state.getDebtPosition(id);"
           " if (user.allCreditPositionsForSaleDisabled || !creditPosition.forSale) revert NF(); }")
    sell = ("function validateSellCreditMarket(State storage state, P calldata params) external view {"
            " state.getCreditPosition(id); state.getDebtPosition(id); if (tenor > max) revert R(); }")
    d = tmp_path / DIR
    d.mkdir(parents=True)
    (d / "BuyCreditMarket.sol").write_text("contract BuyCreditMarket {\n" + buy + "\n}\n")
    (d / "SellCreditMarket.sol").write_text("contract SellCreditMarket {\n" + sell + "\n}\n")
    items = [
        {"id": "function:BuyCreditMarket:validateBuyCreditMarket#a", "kind": "function",
         "contract": "BuyCreditMarket", "name": "validateBuyCreditMarket",
         "file": f"{DIR}/BuyCreditMarket.sol",
         "signature": "function validateBuyCreditMarket(State storage state, P calldata params) external view",
         "visibility": "external", "mutability": "view", "modifiers": [], "in_scope": True,
         "source_span": {"start_line": 2, "end_line": 3}},
        {"id": "function:SellCreditMarket:validateSellCreditMarket#b", "kind": "function",
         "contract": "SellCreditMarket", "name": "validateSellCreditMarket",
         "file": f"{DIR}/SellCreditMarket.sol",
         "signature": "function validateSellCreditMarket(State storage state, P calldata params) external view",
         "visibility": "external", "mutability": "view", "modifiers": [], "in_scope": True,
         "source_span": {"start_line": 2, "end_line": 3}},
    ]
    man = tmp_path / "coverage_manifest.json"
    man.write_text(json.dumps({"items": items}))
    return man


def test_audit_research_only_flags_and_anchor(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    monkeypatch.setattr(ccs.sfp, "ROOT", tmp_path, raising=False)
    # the body extractor reads ROOT/file; point the sibling audit module's ROOT at tmp too
    import sibling_function_parity_audit as sfa
    monkeypatch.setattr(sfa, "ROOT", tmp_path)
    man = _write_manifest(tmp_path)
    monkeypatch.setattr(sys, "argv", ["x", "--manifest", str(man), "--quiet"])
    audit.main()
    rep = json.loads((tmp_path / "output" / "cross_contract_sibling_parity_audit.json").read_text())
    assert rep["is_gate"] is False and rep["research_only"] is True
    assert rep["routes_in_production"] is False and rep["routed_manifest_ids"] == []
    anchor = [c for c in rep["candidates"] if c["weak_contract"] == "SellCreditMarket"
              and "forsale" in c["missing_component"] and c["confidence"] == "high"]
    assert anchor, rep["candidates"]


@pytest.mark.skipif(not (ROOT / "audits/size-credit-2024-06/output/coverage_manifest.json").exists(),
                    reason="size manifest not present")
def test_size_manifest_has_anchor_pair():
    man = ROOT / "audits/size-credit-2024-06/output/coverage_manifest.json"
    names = {(it["contract"], it["name"]) for it in json.loads(man.read_text())["items"]}
    assert ("BuyCreditMarket", "validateBuyCreditMarket") in names
    assert ("SellCreditMarket", "validateSellCreditMarket") in names
