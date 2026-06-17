"""Tests for the registry_position_lifecycle research lens (deterministic, no LLM, no network)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import registry_position_lifecycle_taxonomy as rpl  # noqa: E402
import registry_position_lifecycle_audit as audit  # noqa: E402
import audit_context  # noqa: E402


def _f(name, snippet, visibility="public", mutability=""):
    return rpl.extract_registry_features(name, "", snippet, visibility=visibility, mutability=mutability)


# ---------- CATCH ----------

def test_h23_missing_registry_update_high():
    """NOYA H-23: transferBetweenAccounts mutates the proxy like openBorrowPosition but omits registry update."""
    openp = _f("openBorrowPosition",
               "borrowPositionProxy.openBorrowPosition(0, accountId, marketId, w); "
               "registry.updateHoldingPosition(vaultId, registry.calculatePositionId(x), d, '', true);")
    transfer = _f("transferBetweenAccounts",
                  "borrowPositionProxy.transferBetweenAccounts(accountId, 0, marketId, w);")
    cands = rpl.classify_contract([openp, transfer], "DolomiteConnector")
    assert any(c["shape"] == "missing_registry_update" and c["function"] == "transferBetweenAccounts"
               and c["confidence"] == "high" for c in cands), cands


def test_h18_unguarded_registry_remove_medium():
    """NOYA H-18: closeBorrowPosition removes unguarded; withdraw guards the same remove."""
    withdraw = _f("withdraw",
                  "depositWithdrawalProxy.withdraw(marketId, a); (uint[] memory markets,,,)=dm.getAccountBalances(x);"
                  " if (markets.length == 0) { registry.updateHoldingPosition(vaultId, id, d, '', true); }")
    close = _f("closeBorrowPosition",
               "borrowPositionProxy.closeBorrowPosition(accountId, 0, marketIds);"
               " registry.updateHoldingPosition(vaultId, id, d, '', true);")
    cands = rpl.classify_contract([withdraw, close], "DolomiteConnector")
    assert any(c["shape"] == "unguarded_registry_remove" and c["function"] == "closeBorrowPosition"
               and c["confidence"] == "medium" for c in cands), cands


# ---------- HARMLESS / FP controls ----------

def test_enumerable_set_remove_not_flagged():
    """destinations.remove() (EnumerableSet) is a generic collection op, not a position-subject call."""
    add = _f("addDestinations", "destinations.add(d); registry.register(d);")
    rem = _f("removeDestinations", "destinations.remove(d);")
    cands = rpl.classify_contract([add, rem], "LMPDestinations")
    assert all(c["function"] != "removeDestinations" for c in cands), cands


def test_amount_op_omitter_not_flagged():
    """borrow (amount verb) on a shared proxy without registry update is NOT a lifecycle desync."""
    supply = _f("supply", "aavePool.supply(t, a); registry.updateHoldingPosition(vaultId, id, d, '', false);")
    borrow = _f("borrow", "aavePool.borrow(t, a);")
    cands = rpl.classify_contract([supply, borrow], "AaveConnector")
    assert all(c["function"] != "borrow" for c in cands), cands


def test_open_with_true_not_unguarded_remove():
    """openBorrowPosition passes removePosition=true but is an OPEN, not a remove -> not Shape 2."""
    withdraw = _f("withdraw", "p.withdraw(a); if (markets.length == 0) { registry.updateHoldingPosition(v,i,d,'',true); }")
    openp = _f("openBorrowPosition", "borrowPositionProxy.openBorrowPosition(0,a,m,w); registry.updateHoldingPosition(v,i,d,'',true);")
    cands = rpl.classify_contract([withdraw, openp], "DolomiteConnector")
    assert all(c["shape"] != "unguarded_registry_remove" or c["function"] != "openBorrowPosition"
               for c in cands), cands


def test_view_omitter_suppressed():
    upd = _f("openPosition", "proxy.openPosition(x); registry.updateHoldingPosition(v,i,d,'',true);")
    getter = _f("getPositionTVL", "proxy.transferStuff(x);", mutability="view")
    cands = rpl.classify_contract([upd, getter], "C")
    assert all(c["function"] != "getPositionTVL" for c in cands), cands


def test_no_registry_updater_no_candidate():
    a = _f("foo", "proxy.transferThing(x);")
    b = _f("bar", "proxy.openThing(x);")
    assert rpl.classify_contract([a, b], "C") == []


def test_shape_c_keymismatch_not_claimed():
    """A single-function msg.sender vs calculatorConnector key mismatch (H-12) is Shape-C territory, not ours."""
    f = _f("updateHoldingPosition",
           "bytes32 id = keccak256(abi.encode(msg.sender, p, d)); x = holdingPositions[i].calculatorConnector;")
    # single function, no sibling lifecycle omitter -> no registry_position_lifecycle candidate
    assert rpl.classify_contract([f], "Registry") == []


# ---------- end-to-end (research-only contract) ----------

def test_audit_research_only_flags_and_anchor(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    import sibling_function_parity_audit as sfa
    monkeypatch.setattr(sfa, "ROOT", tmp_path)
    src = ("contract DolomiteConnector {\n"
           "function openBorrowPosition(uint256 m, uint256 w, uint256 a) public {\n"
           "  borrowPositionProxy.openBorrowPosition(0, a, m, w);\n"
           "  registry.updateHoldingPosition(vaultId, registry.calculatePositionId(x), d, \"\", true);\n"
           "}\n"
           "function transferBetweenAccounts(uint256 a, uint256 m, uint256 w) public {\n"
           "  borrowPositionProxy.transferBetweenAccounts(a, 0, m, w);\n"
           "}\n}\n")
    (tmp_path / "DolomiteConnector.sol").write_text(src)
    sl = lambda key: next(i + 1 for i, ln in enumerate(src.split("\n")) if key in ln)
    items = []
    for nm in ("openBorrowPosition", "transferBetweenAccounts"):
        items.append({"id": f"function:DolomiteConnector:{nm}#x", "kind": "function",
                      "contract": "DolomiteConnector", "name": nm, "file": "DolomiteConnector.sol",
                      "signature": f"function {nm}(...) public", "visibility": "public", "mutability": "",
                      "modifiers": [], "in_scope": True,
                      "source_span": {"start_line": sl(f"function {nm}("), "end_line": len(src.split("\n"))}})
    man = tmp_path / "coverage_manifest.json"
    man.write_text(json.dumps({"items": items}))
    monkeypatch.setattr(sys, "argv", ["x", "--manifest", str(man), "--quiet"])
    audit.main()
    rep = json.loads((tmp_path / "output" / "registry_position_lifecycle_audit.json").read_text())
    assert rep["is_gate"] is False and rep["research_only"] is True
    assert rep["routes_in_production"] is False and rep["routed_manifest_ids"] == []
    assert any(c["function"] == "transferBetweenAccounts" and c["shape"] == "missing_registry_update"
               and c["confidence"] == "high" for c in rep["candidates"]), rep["candidates"]
