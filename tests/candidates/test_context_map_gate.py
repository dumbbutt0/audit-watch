"""Gate 3 (context_map) tests — callable surface + state mutation map for the multicall candidate."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "candidates"))
from gates import context_map_gate as g  # noqa: E402

TARGET = "audits/size-credit-2024-06/contracts/2024-06-size"
MULTICALL = "audits/size-credit-2024-06/contracts/2024-06-size/contracts/libraries/Multicall.sol"
SIZE = "audits/size-credit-2024-06/contracts/2024-06-size/contracts/Size.sol"

SNIPPET = ("function multicall(...) {\n uint256 borrowATokenSupplyBefore = ...;\n uint256 debtTokenSupplyBefore = ...;\n"
           " uint256 borrowATokenSupplyAfter = ...;\n uint256 debtTokenSupplyAfter = ...;\n}")


def _cand():
    return {"detector": "multicall_invariant", "function": "multicall", "contract": "Multicall",
            "candidate_surface": "Multicall.multicall", "file": MULTICALL, "code_snippet": SNIPPET}


def test_context_map_collects_terms_and_surface():
    cs, sm, state = g.run(_cand(), TARGET, facade_files=[SIZE])
    assert state == "CONTEXT_MAPPED"
    # state mutation map: real refs found
    assert any("SizeStorage.sol:94" in r for r in sm["isMulticall_refs"])
    assert any("Deposit.sol:80" in r for r in sm["isMulticall_refs"])  # the cap-skip site
    assert sm["final_invariant_refs"]  # validateBorrowATokenIncreaseLteDebtTokenDecrease found
    assert set(sm["before_after_variables"]) >= {
        "borrowATokenSupplyBefore", "borrowATokenSupplyAfter", "debtTokenSupplyBefore", "debtTokenSupplyAfter"}
    # callable surface restricted to the facade file, includes payable accounting fns
    funcs = {c["function"] for c in cs["callable_subcalls"]}
    assert {"deposit", "withdraw", "repay"} <= funcs
    dep = next(c for c in cs["callable_subcalls"] if c["function"] == "deposit")
    assert dep["mutability"] == "payable" and dep["mutates_accounting"] is True


def test_callable_surface_unrestricted_falls_back_to_all():
    cs, sm, state = g.run(_cand(), TARGET, facade_files=None)
    assert state == "CONTEXT_MAPPED"
    assert cs["callable_subcalls_total"] >= 18  # whole repo
