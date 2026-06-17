"""Gate 2 (reachability) tests — Size.sol facade discovery + unresolved internal."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "candidates"))
from gates import reachability_gate as g  # noqa: E402

TARGET = "audits/size-credit-2024-06/contracts/2024-06-size"
MULTICALL = "audits/size-credit-2024-06/contracts/2024-06-size/contracts/libraries/Multicall.sol"


def test_finds_public_facade_for_multicall():
    cand = {"function": "multicall", "file": MULTICALL, "candidate_surface": "Multicall.multicall", "visibility": "internal"}
    body, state = g.run(cand, TARGET)
    assert state == "REACHABLE"
    assert body["attacker_can_reach"] is True
    assert body["external_facade_found"] is True
    # the Size.sol public payable facade is present
    files = [e["file"] for e in body["entrypoints"]]
    assert any(f.endswith("Size.sol") for f in files)
    size = next(e for e in body["entrypoints"] if e["file"].endswith("Size.sol"))
    assert size["visibility"] == "public" and size["payable"] is True
    assert "whenNotPaused" in size["modifiers"]
    assert body["call_path"]  # non-empty chain


def test_unresolved_internal_function_needs_context():
    cand = {"function": "someInternalHelperXyz", "file": MULTICALL,
            "candidate_surface": "Multicall.someInternalHelperXyz", "visibility": "internal"}
    body, state = g.run(cand, TARGET)
    assert state == "NEEDS_CONTEXT"
    assert body["attacker_can_reach"] is None
    assert body["reachability_verdict"] == "UNRESOLVED"
