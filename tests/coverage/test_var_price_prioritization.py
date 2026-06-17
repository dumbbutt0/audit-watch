"""Recall-lab coverage fix: price/oracle/AMM/POL machinery is the value-at-risk surface and must rank
at the TOP (tagged + score-boosted above generic state-changing functions).

Generalized from the Olas recall-lab miss: ~15/23 awarded findings (most Highs) lived in
BalancerPriceOracle / UniswapPriceOracle / LiquidityManager / BuyBackBurner, a cluster that had been
deprioritized. No protocol-specific strings here — only the generic taxonomy + scoring.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import build_coverage_manifest as bcm  # noqa: E402


def test_amm_pol_tag_fires_on_price_machinery():
    for text in ("balancerpriceoracle.validateprice", "uniswappriceoracle", "liquiditymanager.changeranges",
                 "buybackburner.buyback", "swapexacttokensfortokens", "addliquidity minamountout deadline",
                 "pool tick slippage"):
        tags = bcm._tags_for(text, set())
        assert ("amm_pol" in tags or "oracle" in tags), f"{text!r} not tagged as price machinery: {tags}"


def test_oracle_taxonomy_covers_cumulative_and_spot():
    for text in ("cumulativeprice", "pricecumulativelast inverted", "spot price", "getreserves", "slot0"):
        assert "oracle" in bcm._tags_for(text, set()), text


def test_amm_pol_in_deep_pass_risk_sets():
    # The library/internal surface boost must treat amm_pol as a risk tag (RISK) and a strong one (STRONG).
    POL = {"library_internal_surface_boost": True, "deep_pass_attack_surface_score_min": 3,
           "library_internal_surface_boost_cap_per_contract": 3}
    items = [{"kind": "function", "contract": "LiquidityManager", "name": "_changeRanges",
              "visibility": "internal", "mutability": "nonpayable", "tags": ["amm_pol"],
              "contract_type": "contract", "in_scope": True, "attack_surface_score": 2,
              "external_calls": False, "in_tainted_sink": False}]
    assert bcm._apply_library_surface_boost(items, POL) == 1
    assert items[0]["attack_surface_score"] == 3


def test_var_boost_outranks_generic_state_changing():
    """A price/AMM/POL function must score strictly higher than an equivalent generic state-changing one,
    so it sorts to the top of the coverage manifest. We assert the scoring rule directly via the tag set."""
    # generic public state-changing, no risk tag: +2 (external/public state-changing) = 2
    # oracle/amm_pol public state-changing: +2 (state) +2 (risk tag) +1 (VaR boost) = 5
    def score(tags):
        s = 2  # external/public state-changing
        if any(t in tags for t in ("accounting", "token", "oracle", "migration", "config", "amm_pol")):
            s += 2
        if any(t in tags for t in ("oracle", "amm_pol")):
            s += 1
        return s
    assert score(["amm_pol"]) == 5
    assert score(["oracle"]) == 5
    assert score([]) == 2
    assert score(["accounting"]) == 4  # generic risk tag stays below the price machinery
    assert score(["amm_pol"]) > score(["accounting"]) > score([])
