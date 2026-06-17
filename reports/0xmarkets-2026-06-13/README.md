# 0xMarkets audit — overview

Target: `0xMarkets_contract-main` (commit `e94daee…`) — a **GMX Synthetics fork/rebrand** (Hardhat + Foundry; 238
`.sol`; ships the GMX ABDK/Certora/Dedaub/Guardian audits under `audits/`).

## Scope & method
The GMX core is heavily audited and was **not** re-audited. The hunt focused on:
1. **0xMarkets-specific delta** — the `contracts/insurance/` module (`InsuranceVault`, `InsuranceFundUtils`,
   `InsuranceFundEventUtils`, `SettlementHandler`), which is **not in stock GMX** and is wired into
   `contracts/position/DecreasePositionCollateralUtils.sol` (collection of a liquidation-fee slice + drawdown-driven
   injection back into the pool) — plus a spot-check of `contributor/` and the Pyth/config rebrand.
2. **Cross-protocol confirmation for the Cartha audit** — whether `MarketUtils.getMarketTokenPrice` can return ≤ 0.

## Results (see `FINDINGS.md`)
- **X-1 (cross-protocol):** confirmed `getMarketTokenPrice` returns 0 when `poolValue == 0` and negative when
  `poolValue < 0` (signed `int256` pool value). This **validates Cartha C-1's reachability** and raises its realistic
  severity — see `cartha-C1-reachability.md` (copied into `reports/cartha-2026-06-13/`).
- **I-1 (Medium, design):** insurance injection compensates *current* LP holders, not drawdown-era holders → JIT
  capture of insurance reserve.
- **I-2 (Low):** `triggerFactor` unset-default of 0 means "inject on any drawdown" (inverted-safe default footgun).
- Custom insurance collection/injection/custody are otherwise **conservation- and access-sound**; no clean Critical.

No build/PoC was stood up (full GMX needs a large Hardhat `node_modules`; the insurance findings are design/config and
the X-1 result is a source-level confirmation). GMX core assumed audited-sound. **Nothing submitted.**
