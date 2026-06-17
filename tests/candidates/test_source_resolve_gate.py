"""Gate 1 (source_resolve) tests — real Size source + missing/mismatch cases."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "candidates"))
from gates import source_resolve_gate as g  # noqa: E402

TARGET = "audits/size-credit-2024-06/contracts/2024-06-size"
MULTICALL = "audits/size-credit-2024-06/contracts/2024-06-size/contracts/libraries/Multicall.sol"


def _cand(file=MULTICALL, fn="multicall", line=26):
    return {"detector": "multicall_invariant", "contract": "Multicall", "function": fn, "file": file, "line": line}


def test_resolves_real_function():
    body, state = g.run(_cand(), TARGET)
    assert state == "RESOLVED_SOURCE"
    assert body["resolution_status"] == "resolved"
    assert body["line_range"][0] == 26 and body["line_range"][1] >= 40
    assert body["function_signature"].startswith("function multicall(")
    assert body["source_hash"] == "md5:cecf083ad025a572e8e8766a6e86c1c4"
    assert "functionDelegateCall(address(this)" in body["code_snippet"]
    assert "validateBorrowATokenIncreaseLteDebtTokenDecrease" in body["code_snippet"]


def test_missing_file_needs_context():
    body, state = g.run(_cand(file="audits/size-credit-2024-06/contracts/does/not/exist.sol"), TARGET)
    assert state == "NEEDS_CONTEXT"
    assert body["resolution_status"] == "unresolved"
    assert body["source_hash"] is None


def test_present_file_absent_function_killed():
    body, state = g.run(_cand(fn="thisFunctionDoesNotExist"), TARGET)
    assert state == "KILLED"
    assert body["resolution_status"] == "function_not_found"
    assert body["source_hash"] is not None  # file was found
