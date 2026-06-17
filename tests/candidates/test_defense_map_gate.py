"""Gate 4 (defense_map) tests — real Size multicall defenses."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "candidates"))
from gates import reachability_gate, context_map_gate, defense_map_gate  # noqa: E402

TARGET = "audits/size-credit-2024-06/contracts/2024-06-size"
MULTICALL = "audits/size-credit-2024-06/contracts/2024-06-size/contracts/libraries/Multicall.sol"
SIZE = "audits/size-credit-2024-06/contracts/2024-06-size/contracts/Size.sol"


def _stage1():
    cand = {"detector": "multicall_invariant", "contract": "Multicall", "function": "multicall",
            "candidate_surface": "Multicall.multicall", "file": MULTICALL, "line": 26, "visibility": "internal",
            "code_snippet": "uint256 borrowATokenSupplyBefore; uint256 debtTokenSupplyAfter;"}
    reach, _ = reachability_gate.run(cand, TARGET)
    cs, sm, _ = context_map_gate.run(cand, TARGET, facade_files=[SIZE])
    return cand, reach, cs, sm


def test_defense_map_status_and_facade_modifier():
    cand, reach, cs, sm = _stage1()
    body, state = defense_map_gate.run(cand, TARGET, reach, cs, sm)
    assert state == "DEFENSE_MAPPED" and body["status"] == "DEFENSE_MAPPED"
    size_ep = [e for e in body["entrypoint_defenses"] if e["file"].endswith("Size.sol")]
    assert size_ep and "whenNotPaused" in size_ep[0]["modifiers"]
    assert size_ep[0]["anyone_can_call"] is True


def test_defense_map_finds_ismulticall_cap_skip():
    cand, reach, cs, sm = _stage1()
    body, _ = defense_map_gate.run(cand, TARGET, reach, cs, sm)
    assert "validateBorrowATokenCap" in body["checks_skipped_when_isMulticall"]
    skips = [b for b in body["is_multicall_branches"] if b["branch_kind"] == "skip_in_multicall"]
    assert any(b["file"].endswith("Deposit.sol") and b["check_skipped_or_changed"] == "validateBorrowATokenCap"
               and b["coverage_status"] == "partially_covers_candidate" for b in skips)


def test_defense_map_records_final_invariant_and_matrix():
    cand, reach, cs, sm = _stage1()
    body, _ = defense_map_gate.run(cand, TARGET, reach, cs, sm)
    names = {a["name"] for a in body["accounting_defenses"]}
    assert "validateBorrowATokenIncreaseLteDebtTokenDecrease" in names
    assert "validateBorrowATokenCap" in names
    assert body["guard_coverage_matrix"]  # non-empty
    assert body["defenses"] and "checks_skipped_when_isMulticall" in body  # alias keys for dashboard
    assert body["hard_blockers"] == []  # defense gate does not hard-kill at this stage
