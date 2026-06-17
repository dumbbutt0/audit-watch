"""P130: general behavior of the library/internal risk-logic surface boost.

No protocol-specific strings. Validates the two-signal, capped, reversible repair in
build_coverage_manifest._apply_library_surface_boost.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import build_coverage_manifest as bcm  # noqa: E402

POL = {"library_internal_surface_boost": True, "deep_pass_attack_surface_score_min": 3,
       "library_internal_surface_boost_cap_per_contract": 3}


def _fn(contract, name, score, *, vis="internal", mut="view", tags=(), ctype="library",
        in_scope=True, ext=False, sink=False):
    return {"kind": "function", "contract": contract, "name": name, "visibility": vis,
            "mutability": mut, "tags": list(tags), "contract_type": ctype, "in_scope": in_scope,
            "attack_surface_score": score, "external_calls": ext, "in_tainted_sink": sink}


def test_internal_risk_logic_is_boosted_to_cutoff():
    items = [_fn("LibOracle", "getPrice", 2, tags=["oracle"])]
    n = bcm._apply_library_surface_boost(items, POL)
    assert n == 1
    assert items[0]["attack_surface_score"] == 3
    assert items[0]["surface_boost"] == "library_internal_risk"


def test_public_view_helper_with_accounting_tag_is_boosted():
    # not internal, but view + accounting tag => computation/helper logic
    items = [_fn("ConnectorA", "totalValue", 2, vis="public", mut="view",
                 tags=["accounting"], ctype="contract")]
    assert bcm._apply_library_surface_boost(items, POL) == 1
    assert items[0]["attack_surface_score"] == 3


def test_facet_internal_logic_is_boosted():
    items = [_fn("SomethingFacet", "_settle", 2, tags=["token"], ctype="contract")]
    assert bcm._apply_library_surface_boost(items, POL) == 1


def test_no_risk_tag_is_not_boosted():
    # single signal (helper) without the second signal (risk tag) => untouched (FP-tight)
    items = [_fn("LibMath", "_mulDiv", 1, tags=[])]
    assert bcm._apply_library_surface_boost(items, POL) == 0
    assert items[0]["attack_surface_score"] == 1


def test_non_helper_state_changing_is_not_affected_by_boost():
    # an external state-changing fn already scores high; boost only targets sub-cutoff helper logic
    items = [_fn("Vault", "withdraw", 2, vis="external", mut="", tags=["accounting"], ctype="contract")]
    # external + non-view + not library/facet => not "helper"; should not be boosted by this rule
    assert bcm._apply_library_surface_boost(items, POL) == 0


def test_already_high_score_is_left_alone():
    items = [_fn("LibOracle", "getPrice", 4, tags=["oracle"])]
    assert bcm._apply_library_surface_boost(items, POL) == 0
    assert items[0]["attack_surface_score"] == 4


def test_out_of_scope_is_not_boosted():
    items = [_fn("LibOracle", "getPrice", 2, tags=["oracle"], in_scope=False)]
    assert bcm._apply_library_surface_boost(items, POL) == 0


def test_per_contract_cap_bounds_inflation():
    items = [_fn("LibBig", f"f{i}", 2, tags=["oracle"]) for i in range(10)]
    n = bcm._apply_library_surface_boost(items, POL)
    assert n == 3  # cap_per_contract
    assert sum(1 for it in items if it["attack_surface_score"] == 3) == 3


def test_flag_off_is_fully_reversible():
    items = [_fn("LibOracle", "getPrice", 2, tags=["oracle"])]
    n = bcm._apply_library_surface_boost(items, {**POL, "library_internal_surface_boost": False})
    assert n == 0
    assert items[0]["attack_surface_score"] == 2
    assert "surface_boost" not in items[0]


# ---------------------------------------------------------------------------
# P132 — noise trims: mock exclusion + trivial-body exclusion
# ---------------------------------------------------------------------------

def _mk(contract, name, *, file="contracts/X.sol", tags=("oracle",), trivial=False,
        score=2, vis="internal", mut="view", ctype="library"):
    it = _fn(contract, name, score, vis=vis, mut=mut, tags=tags, ctype=ctype)
    it["file"] = file
    it["trivial_body"] = trivial
    return it


# --- _is_mock_item ---
def test_mock_glob_file_still_excluded():
    assert bcm._is_mock_item(_mk("Foo", "f", file="contracts/MockOracle.sol")) is True


def test_starmock_filename_excluded():  # ConnectorMock2.sol style
    assert bcm._is_mock_item(_mk("ConnectorMock2", "f", file="contracts/helpers/ConnectorMock2.sol")) is True


def test_contract_name_mock_excluded_even_if_file_not_mock_prefixed():
    assert bcm._is_mock_item(_mk("ConnectorMock2", "f", file="contracts/helpers/Helper.sol")) is True


def test_mock_path_segment_excluded():
    assert bcm._is_mock_item(_mk("Foo", "f", file="contracts/test/Foo.sol")) is True


def test_legit_contract_not_flagged_as_mock():
    assert bcm._is_mock_item(_mk("ChainlinkOracleConnector", "getValue",
                                 file="contracts/oracles/ChainlinkOracleConnector.sol")) is False


# --- _is_trivial_body ---
def test_trivial_empty_array_return():
    assert bcm._is_trivial_body("function f() public pure returns (address[] memory) { return new address[](0); }") is True


def test_trivial_address_zero_return():
    assert bcm._is_trivial_body("function f() public view returns (address) { return address(0); }") is True


def test_trivial_literal_returns():
    for lit in ("0", "1", "true", "false", '""', "''", "SOME_CONSTANT"):
        assert bcm._is_trivial_body("function f() public pure returns (uint) { return %s; }" % lit) is True, lit


def test_trivial_empty_body():
    assert bcm._is_trivial_body("function f() external {}") is True


def test_nontrivial_body_with_call_or_math_kept():
    assert bcm._is_trivial_body(
        "function _getValue(uint a) internal view returns (uint) { return oracle.getPrice(a) * w / total; }") is False
    assert bcm._is_trivial_body(
        "function f() internal view returns (uint) { uint x = a[i]; return x + 1; }") is False
    # comments must not flip a real body to trivial
    assert bcm._is_trivial_body(
        "function f() internal returns (uint) { // return 0;\n return compute(a, b); }") is False


# --- boost integration ---
def test_mock_helper_not_boosted():
    items = [_mk("ConnectorMock2", "getPositionTVL", file="contracts/helpers/ConnectorMock2.sol")]
    assert bcm._apply_library_surface_boost(items, POL) == 0
    assert items[0]["attack_surface_score"] == 2


def test_trivial_helper_not_boosted():
    items = [_mk("AaveConnector", "_getUnderlyingTokens", trivial=True, tags=["token"])]
    assert bcm._apply_library_surface_boost(items, POL) == 0


def test_nontrivial_oracle_helper_still_boosted():
    items = [_mk("NoyaValueOracle", "_getValue", trivial=False, tags=["oracle"])]
    assert bcm._apply_library_surface_boost(items, POL) == 1
    assert items[0]["attack_surface_score"] == 3


def test_getpositiontvl_style_still_boosted():
    items = [_mk("BalancerConnector", "_getPositionTVL", trivial=False, tags=["accounting"],
                 file="contracts/connectors/BalancerConnector.sol", vis="public")]
    assert bcm._apply_library_surface_boost(items, POL) == 1


def test_strong_tags_ranked_before_weak_under_cap():
    # cap=1: the oracle-tagged (strong) fn wins over a config-only (weak) fn in the same contract
    items = [_fn("LibX", "weak", 2, tags=["config"]), _fn("LibX", "strong", 2, tags=["oracle"])]
    pol = {**POL, "library_internal_surface_boost_cap_per_contract": 1}
    assert bcm._apply_library_surface_boost(items, pol) == 1
    strong = next(it for it in items if it["name"] == "strong")
    weak = next(it for it in items if it["name"] == "weak")
    assert strong["attack_surface_score"] == 3 and weak["attack_surface_score"] == 2
