# Olas (Code4rena 2026-01) — AWARDED Findings (revealed at reveal-time from code4rena.com/reports/2026-01-olas)

> Source: the consolidated C4 awarded report (NOT the Zellic-V12 set, which C4 declared out of scope; that is preserved in v12_findings_OOS.md).

# High Risk Findings (11)

## [[H-01] Broken TWAP validation allows spot-price manipulation and renders slippage checks ineffective](https://code4rena.com/reports/2026-01-olas)
## [[H-02] Variable overwrite](https://code4rena.com/reports/2026-01-olas)
## [[H-03] Balancer oracle uses vault balances as price and can be steered by anyone](https://code4rena.com/reports/2026-01-olas)
## [[H-04] Incorrect TWAP calculation in BalancerPriceOracle allows price manipulation](https://code4rena.com/reports/2026-01-olas)
## [[H-05] Insolvency via Cross-Service Reentrancy in StakingBase._withdraw](https://code4rena.com/reports/2026-01-olas)
## [[H-06] Service owner can steal protocol tokens by exploiting reentrancy in create](https://code4rena.com/reports/2026-01-olas)
## [[H-07] Missing deadline parameter in register signatures](https://code4rena.com/reports/2026-01-olas)
## [[H-08] Critical logic inversion in price guard allows flash-loan manipulation of liquidity operations](https://code4rena.com/reports/2026-01-olas)
## [[H-09] Missing maximum bond signature parameter](https://code4rena.com/reports/2026-01-olas)
## [[H-10] Token callback reentrancy](https://code4rena.com/reports/2026-01-olas)
## [[H-11] cumulativePrice is corrupted when price updates are rejected](https://code4rena.com/reports/2026-01-olas)

# Medium Risk Findings (12)

## [[M-01] Arbitrum retryable-ticket refund/value not verified enables timelock ETH exfiltration](https://code4rena.com/reports/2026-01-olas)
## [[M-02] Uniswap oracle validatePrice can be griefed per block](https://code4rena.com/reports/2026-01-olas)
## [[M-03] priceCumulativeLast is used inverted in Uniswap Oracle](https://code4rena.com/reports/2026-01-olas)
## [[M-04] DoS in liquidity migration due to unit mismatch in UniswapPriceOracle](https://code4rena.com/reports/2026-01-olas)
## [[M-05] BalancerPriceOracle::validatePrice uses stale TWAP](https://code4rena.com/reports/2026-01-olas)
## [[M-06] changeRanges silently fails when price is out of tick range, sending all liquidity to treasury](https://code4rena.com/reports/2026-01-olas)
## [[M-07] Malicious user can prevent buying back OLAS token via Slipstream](https://code4rena.com/reports/2026-01-olas)
## [[M-08] Incorrect proportional reward splits when an operator has been slashed](https://code4rena.com/reports/2026-01-olas)
## [[M-09] checkpoint() does not correct effectiveBond downward](https://code4rena.com/reports/2026-01-olas)
## [[M-10] Services can earn undeserved rewards by manipulating checkpoint timing during reward droughts](https://code4rena.com/reports/2026-01-olas)
## [[M-11] No slippage protection on Uniswap swap](https://code4rena.com/reports/2026-01-olas)
## [[M-12] Balancer oracle deadlock from cumulative price weight](https://code4rena.com/reports/2026-01-olas)
