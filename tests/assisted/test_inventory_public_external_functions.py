"""P103: in-scope function inventory — RESEARCH-ONLY, un-wired. Proves all public/external functions are
inventoried (the recall fix for the P102 selection bottleneck), constructors are separated, and internal/private
are excluded from the enumeration surface."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import inventory_public_external_functions as INV  # noqa: E402

SAMPLE = """
contract A {
    constructor(uint256 x) payable {}
    function f1() public {}
    function f2(uint256 v) external view returns (uint256) { return v; }
    function f3() internal {}
    function f4() private pure returns (bool) { return true; }
    function f5() returns (uint256) { return 1; }
}
interface IB { function ig() external; }
library L { function lh() internal pure returns (uint256) { return 0; } }
"""


def test_self_test_passes():
    assert INV._self_test() == 0


def _inv(tmp_path):
    (tmp_path / "A.sol").write_text(SAMPLE)
    return INV.inventory(tmp_path)


def test_inventories_public_external(tmp_path):
    r = _inv(tmp_path)
    pe = {(f["contract"], f["function"]) for f in r["public_external"]}
    assert ("A", "f1") in pe and ("A", "f2") in pe and ("IB", "ig") in pe


def test_excludes_internal_private_from_surface(tmp_path):
    r = _inv(tmp_path)
    pe = {f["function"] for f in r["public_external"]}
    assert "f3" not in pe and "f4" not in pe and "lh" not in pe and "f5" not in pe  # f5 defaults to internal


def test_constructors_separated(tmp_path):
    r = _inv(tmp_path)
    assert any(f["is_constructor"] and f["contract"] == "A" for f in r["constructors"])
    assert all(not f["is_constructor"] for f in r["public_external"])


def test_visibility_and_mutability_and_span(tmp_path):
    r = _inv(tmp_path)
    f2 = [f for f in r["functions"] if f["function"] == "f2"][0]
    assert f2["visibility"] == "external" and f2["mutability"] == "view"
    assert len(f2["source_span"]) == 2 and f2["source_span"][0] >= 1


def test_iqai_inventory_includes_moveliquidity():
    """The P102 locus must be in the public/external inventory regardless of the lens."""
    src = Path("/tmp/p102-inscope")
    if not src.is_dir():
        import pytest
        pytest.skip("IQ-AI clone not present")
    r = INV.inventory(src)
    pe = {(f["contract"], f["function"]) for f in r["public_external"]}
    assert ("LiquidityManager", "moveLiquidity") in pe


def test_flags_unwired():
    assert INV.FLAGS["is_gate"] is False and INV.FLAGS["routes_in_production"] is False
