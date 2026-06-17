"""Tests for the getter-vs-state reconciliation taxonomy/classifier.

This lens is about the correctness of returned information and helper control flow, NOT generic
view-function scanning. Positives assert a real return-shape/ordering/encoding/freshness defect is
caught; FP-controls assert that trivial getters, constant views, units-owned pure math, comments,
and event-only ABI words are NOT tagged.
"""
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

gs = importlib.import_module("getter_state_taxonomy")


def clf(name, snippet, **kw):
    return gs.classify(name, snippet=snippet, **kw)


# --------------------------------------------------------------------------- positives
def test_wrong_state_variable_counter_returns_nonce():
    c = clf("getCounter",
            snippet="return uint256(s.sys.tractor.blueprintNonce[publisher][counterId]);",
            mutability="view")
    assert c["getter_state_sensitive"] is True
    assert c["category"] == "wrong_state_variable"
    assert gs.is_high_risk(c)


def test_wrong_return_order_struct_fields_swapped():
    c = clf("getReserves",
            signature="returns (uint256 reserve0, uint256 reserve1)",
            snippet="return (s.well.reserve1, s.well.reserve0);",
            mutability="view")
    assert c["getter_state_sensitive"] is True
    assert c["category"] in ("wrong_return_order", "view_used_by_state_path")
    assert "multi_return" in c["features"]


def test_abi_encode_decode_helper():
    c = clf("tractor",
            snippet="AdvancedFarmCall[] memory calls = abi.decode(blueprint.data, (AdvancedFarmCall[]));",
            mutability="payable")
    assert c["getter_state_sensitive"] is True
    assert c["category"] in ("abi_encoding_mismatch", "struct_field_mismatch")
    assert "abi" in c["features"] or "struct_token" in c["features"]


def test_calldata_offset_helper():
    c = clf("pasteAdvancedBytes",
            snippet="uint256 off = calldataload(add(returnData.offset, 32)); return off;",
            mutability="pure")
    assert c["getter_state_sensitive"] is True
    assert c["category"] == "calldata_offset_mismatch"


def test_sorting_comparison_helper():
    c = clf("quickSort",
            signature="returns (WellDeltaB[] memory)",
            snippet="if (arr[uint(i)].deltaB > pivot) { swap(arr, i, j); }",
            mutability="pure")
    assert c["getter_state_sensitive"] is True
    assert c["category"] == "sorting_or_ordering_bug"


def test_array_length_mismatch():
    c = clf("balanceOfBatch",
            signature="returns (uint256[] memory)",
            snippet="uint256[] memory r = new uint256[](accounts.length); return r;",
            mutability="view")
    assert c["getter_state_sensitive"] is True
    assert c["category"] == "array_length_mismatch"


def test_transformed_view_value_wrong_scope():
    c = clf("totalDeltaB",
            signature="returns (int256 deltaB)",
            snippet="return LibWellMinting.check(C.BEAN_ETH_WELL);",
            mutability="view")
    assert c["getter_state_sensitive"] is True
    assert c["category"] in ("wrong_return_field", "consumer_assumption_mismatch")
    assert "transformed_return" in c["features"]


def test_cache_vs_storage_mismatch():
    c = clf("getSyncedTotal",
            snippet="uint256 cached = s.totalSupply; _sync(); return cached + s.pendingMint;",
            mutability="view")
    assert c["getter_state_sensitive"] is True
    assert "cache_storage" in c["features"]


def test_view_consumed_by_state_path():
    c = clf("seasonTime",
            signature="returns (uint32)",
            snippet="if (block.timestamp < s.sys.season.start) return 0;"
                    " return uint32((block.timestamp - s.sys.season.start) / s.sys.season.period);",
            mutability="view", consumed_by_state=True)
    assert c["getter_state_sensitive"] is True
    assert c["consumer_hint"] == "consumed_by_state_path"
    assert c["category"] in ("branch_mismatch", "default_value_mismatch", "view_used_by_state_path")


# --------------------------------------------------------------------------- FP controls
def test_fp_trivial_single_var_getter():
    c = clf("owner", signature="returns (address)", snippet="return s.owner;", mutability="view")
    assert c["getter_state_sensitive"] is False


def test_fp_constant_returning_view():
    c = clf("decimals", signature="returns (uint8)", snippet="return 18;", mutability="view")
    assert c["getter_state_sensitive"] is False


def test_fp_pure_math_helper_units_owned():
    c = clf("mulDiv", snippet="return a * b / denominator;", mutability="pure")
    assert c["getter_state_sensitive"] is False


def test_fp_comment_only_mismatch():
    c = clf("getValue",
            snippet="// returns token0 vs token1 in the wrong order, ABI decode bug\n return s.value;",
            mutability="view")
    assert c["getter_state_sensitive"] is False


def test_fp_event_only_abi_word():
    c = clf("notifySorted", snippet="emit Sorted(a, b);", mutability="")
    assert c["getter_state_sensitive"] is False
