"""
Tests for the decimals/units invariant taxonomy + detector (deterministic, no LLM/network).

Catches the decimals/scaling math behind eval miss #184 (the reserve0.mul(1e18).div(reserve1) shape) while
the two-signal rule (unit-context + body arithmetic/call signal) keeps the lens FOCUSED — no flag-all-
arithmetic blowup (the lesson from the token lens). Mirrors tests/token_standard.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
units = importlib.import_module("units_invariant_taxonomy")
audit_mod = importlib.import_module("units_invariant_audit")


def clf(name, snippet, file="contracts/Lib.sol", contract="Lib", signature=""):
    return units.classify(name, signature, file, contract, snippet=snippet)


# ── positive detection: (name, body snippet, expected_category) ──
CATCH = [
    ("normalize", "uint8 d = IERC20Metadata(token).decimals(); amount = amount * 10**(18 - d);", "token_decimals"),
    ("getBeanTokenPriceFromTwaReserves", "price = uint256(s.sys.twaReserves[well].reserve0).mul(1e18).div(s.sys.twaReserves[well].reserve1);", "twa_reserves"),
    ("getEthPrice", "(, int256 answer,,,) = feed.latestRoundData(); uint8 dec = feed.decimals(); price = uint256(answer);", "chainlink_decimals"),
    ("spotPrice", "(uint reserve0, uint reserve1) = pair.getReserves(); price = reserve0.mul(1e18).div(reserve1);", "reserve_units"),
    ("wellBdv", "bdv = amount.mul(price).div(1e6); // bdv units", "bdv_units"),
    ("getAmountOut", "amountOut = amountIn.mul(reserveOut).div(reserveIn.add(amountIn));", "amount_in_out"),
    ("convertShares", "shares = assets.mul(totalShares).div(totalAssets);", "shares_assets"),
    ("wstethRate", "uint256 rate = IWsteth(wsteth).stEthPerToken(); price = amount.mul(rate).div(1e18);", "price_per_share"),
    ("scalePrecision", "value = amount.mul(PRECISION).div(totalSupply); // precision scalar", "precision_constant"),
    ("badPrice", "price = reserve0.div(reserve1).mul(1e18); // div before mul, reserve units", "division_before_multiplication"),
    ("packStalk", "stalk = uint128(bdv.mul(stalkPerBdv)); // downcast after scaling", "downcast_after_scaling"),
]


@pytest.mark.parametrize("name,snip,cat", CATCH)
def test_catches_units_shapes(name, snip, cat):
    c = clf(name, snip)
    assert c["units_sensitive"] is True, f"{name} should be units-sensitive"
    assert c["category"] == cat, f"{name}: expected {cat}, got {c['category']}"


def test_184_shape_is_high_risk():
    c = clf("getBeanTokenPriceFromTwaReserves",
            "price = uint256(s.sys.twaReserves[well].reserve0).mul(1e18).div(s.sys.twaReserves[well].reserve1);")
    assert units.is_high_risk(c)


# ── FP controls: must NOT tag ──
def test_bare_1e18_no_amount_context():
    # a 1e18 constant with no unit context and no scaling arithmetic
    c = clf("setMax", "MAX = 1e18;")
    assert c["units_sensitive"] is False


def test_basis_points_fee_math_not_token_decimals():
    # fee math with 10000 bps and no price/reserve/decimal context
    c = clf("applyFee", "fee = amount * 30 / 10000; total = amount - fee;", contract="Market")
    assert c["category"] != "token_decimals"
    # may be untagged entirely (no unit-context term) — that is the desired outcome
    assert c["units_sensitive"] is False


def test_pure_muldiv_helper_alone():
    c = clf("mulDiv", "return a.mul(b).div(denominator);", file="contracts/Math.sol", contract="LibPRBMath")
    assert c["units_sensitive"] is False


def test_local_loop_division_not_tagged():
    c = clf("average", "for (uint i; i < n; ++i) { sum += arr[i]; } return sum / n;")
    assert c["units_sensitive"] is False


def test_comment_only_not_tagged():
    # 1e18 and 'reserve' appear ONLY in a comment -> stripped before matching
    c = clf("noop", "// price = reserve0.mul(1e18).div(reserve1) would be wrong\n return x;")
    assert c["units_sensitive"] is False


def test_name_alone_no_body_signal_not_tagged():
    # a function named like a rate/price but with no scaling arithmetic in the body
    c = clf("getHumidity", "return s.sys.fert.humidity;", contract="FertilizerFacet")
    assert c["units_sensitive"] is False


# ── end-to-end detector over a synthetic manifest + on-disk source ──
def test_detector_end_to_end(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True)
    (tmp_path / "contracts").mkdir(parents=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setattr(audit_mod, "ROOT", tmp_path)  # source root for snippet reads
    src = ["// header", "library LibWell {",
           "    function getBeanTokenPriceFromTwaReserves(address well) internal view returns (uint256 price) {",
           "        price = uint256(twaReserves[well].reserve0).mul(1e18).div(twaReserves[well].reserve1);",
           "    }",
           "    function plain() internal pure returns (uint256) { return 1; }", "}"]
    (tmp_path / "contracts" / "LibWell.sol").write_text("\n".join(src))
    manifest = {"items": [
        {"id": "function:LibWell:getBeanTokenPriceFromTwaReserves#a", "kind": "function",
         "name": "getBeanTokenPriceFromTwaReserves", "contract": "LibWell", "file": "contracts/LibWell.sol",
         "signature": "function getBeanTokenPriceFromTwaReserves(address well) internal view returns (uint256 price)",
         "source_span": {"start_line": 3, "end_line": 5}, "in_scope": True},
        {"id": "function:LibWell:plain#b", "kind": "function", "name": "plain", "contract": "LibWell",
         "file": "contracts/LibWell.sol", "signature": "function plain() internal pure returns (uint256)",
         "source_span": {"start_line": 6, "end_line": 6}, "in_scope": True},
    ]}
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps(manifest))
    (tmp_path / "output" / "coverage_dispositions.json").write_text(json.dumps(
        {"dispositions": [{"manifest_id": "function:LibWell:getBeanTokenPriceFromTwaReserves#a",
                           "status": "cleared", "clear_reason": "reads only manipulation-resistant TWA reserves"}]}))
    old = sys.argv
    sys.argv = ["units_invariant_audit"]
    try:
        assert audit_mod.main() == 0
    finally:
        sys.argv = old
    rep = json.loads((tmp_path / "output" / "units_invariant_audit.json").read_text())
    names = {d["name"] for d in rep["detected"]}
    assert "getBeanTokenPriceFromTwaReserves" in names and "plain" not in names  # catch + FP control
    cleared = {x["name"] for x in rep["previously_cleared_high_risk"]}
    assert "getBeanTokenPriceFromTwaReserves" in cleared
    assert any("#184" in m for m in rep["likely_eval_miss_classes_recovered"])
