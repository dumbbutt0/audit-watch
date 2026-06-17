# P198 — Centrifuge coverage manifest (read-only, source-grounded, BLIND)

Built by read-only enumeration of `audits/centrifuge-2023-09-holdout/contracts/src` (22 files / 4.1k LOC). **Blind
to finding details** — nothing here uses the answer key (the sealed `report.md` was opened only for a count-only
viability check; finding bodies are read only at scoring, step 6).

## Architecture (RWA liquidity pools)
Pools contain **tranches** (transfer-restricted tranche tokens). Investors place **epoch-based invest/redeem
orders**; fulfillment arrives **from an L2 via `Gateway`/`Messages`** (`handleExecutedCollect*` /
`handleExecutedDecrease*`). An **`Escrow`** holds tranche tokens; a **`UserEscrow`** holds redeemed currency until
claimed. `LiquidityPool` is an **ERC4626-style** wrapper; `InvestmentManager` is the accounting core
(order limits, price/decimal conversion, share/asset payout). `RestrictionManager` gates tranche-token transfers
by membership. `Root`/`PauseAdmin`/`DelayedAdmin`/`Auth` are privileged controls.

## Invariant surfaces (source-grounded)
- **Epoch fulfillment / conservation** — `InvestmentManager.handleExecutedCollectInvest`,
  `handleExecutedCollectRedeem`, `handleExecutedDecreaseInvestOrder`, `handleExecutedDecreaseRedeemOrder`
  (L2-driven payout/refund; share-issued vs currency-paid conservation; escrow movements).
- **Claim / ERC4626 conversion & rounding** — `processDeposit`, `processMint`, `processWithdraw`, `processRedeem`,
  `_calculateTrancheTokenAmount`, `_calculateCurrencyAmount`, `_calculatePrice`, `_toPriceDecimals`/`_fromPriceDecimals`;
  `LiquidityPool.deposit/mint/withdraw/redeem`.
- **Order placement / decrease (refund accounting)** — `requestDeposit`, `requestRedeem`, `decreaseDepositRequest`,
  `decreaseRedeemRequest`, `_decreaseDepositLimits`, `_decreaseRedemptionLimits`.
- **Escrow custody** — `Escrow.approve`; `UserEscrow.transferIn`/`transferOut` (release-to-receiver asymmetry,
  allowance, double-release).
- **Transfer restriction** — `Tranche.transfer/transferFrom/mint` (`restricted` modifier),
  `RestrictionManager.detectTransferRestriction`/`updateMember`/`hasMember`.
- **Cross-chain currency custody** — `PoolManager.handleTransfer`/`transfer`, `Gateway` message routing.
- **Privileged controls** — `Auth`/`rely`/`deny`, `Root`, `PauseAdmin`, `DelayedAdmin`, `file(...)` setters,
  `deployTranche`/`deployLiquidityPool`/`addPool`/`allowPoolCurrency` (`onlyGateway`).

## Pre-registered bounded blind sample (12 highest-invariant-density surfaces)
Frozen **before** the blind run; one Sonnet subagent per surface (deep_trace.md + verbatim source). See
`_sample_manifest.json` for exact line ranges.

| id | surface | invariant role |
|---|---|---|
| IM-01 | InvestmentManager.handleExecutedCollectInvest | epoch invest fulfillment (share issuance + price + escrow) |
| IM-02 | InvestmentManager.handleExecutedCollectRedeem | epoch redeem fulfillment (asset payout + escrow) |
| IM-03 | InvestmentManager.handleExecutedDecreaseInvestOrder | order-decrease refund accounting |
| IM-04 | InvestmentManager.processDeposit | claim shares (conversion/rounding + deposit limits) |
| IM-05 | InvestmentManager.processRedeem | claim assets (escrow transferOut conservation) |
| IM-06 | InvestmentManager._calculateTrancheTokenAmount | price/decimal conversion (rounding/precision) |
| IM-07 | InvestmentManager.decreaseRedeemRequest | redeem-order decrease (refund conservation) |
| ESC-08 | UserEscrow.transferOut | escrow custody release (receiver / double-release asymmetry) |
| ESC-09 | UserEscrow.transferIn | escrow custody intake |
| LP-10 | LiquidityPool.withdraw | ERC4626 withdraw (owner/allowance + payout) |
| TR-11 | Tranche.transfer | restricted transfer (transfer-restriction invariant) |
| RM-12 | RestrictionManager.detectTransferRestriction | membership / transfer-restriction logic |

**Selection rule:** state-mutating + accounting-conservation / epoch / escrow / restriction surfaces (the RWA
invariant core), spread across the distinct subsystems. Bounded (12) → an adjudication-**generalization** signal,
not exhaustive recall. View/pure getters, pure cross-chain plumbing, and ERC20/util helpers were de-prioritized.
