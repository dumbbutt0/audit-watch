# P271 — SCAFFOLD_DESIGN

## Architecture
`pocs/p271/wise/` — isolated foundry project. Wise `contracts/` copied READ-ONLY to `wise_src/`; deps pinned in
`lib/` (forge-std v1.9.6, OZ v4.9.6). `foundry.toml`: solc 0.8.24, evm shanghai, `contracts/=wise_src/` remap, skip
the `@pendle`-importing oracle lib + the contest's own `.t.sol`. No contest/production source mutation.

## Two reusable PoC patterns (the scaffold's core deliverable)
The Wise calibration showed both awarded mechanisms are **accounting-logic asymmetries** provable without a full
deposit→borrow→liquidate runtime. Two reusable patterns emerged:

1. **Inherit-and-expose-internal (Tier B, real production code).** For accounting bugs in internal/abstract helpers
   (FeeManagerHelper bad-debt): a thin `Harness is <ProductionAbstract>` passes minimal ctor args (dummy non-zero
   addresses for stored-only deps + a 1-function mock for any ctor-time external call, here
   `POSITION_NFTS.FEE_MANAGER_NFT()`) and exposes the real internal functions. The PoC then drives the **real
   production statements** (`_increaseTotalBadDebt`/`_setBadDebtPosition`/`_decreaseTotalBadDebt`/`_eraseBadDebtUser`)
   in the exact production sequence, with a corrected-reference control. **No prose; real EVM execution.**

2. **Faithful control-flow reproduction (Tier C).** For bugs in deeply-stateful private functions whose full deploy
   is intractable (WiseCore `_calculateReceiveAmount`): transcribe the **exact branch ordering + the real arithmetic
   formula** from source into a small harness, model the position state, and prove the wrong transition vs a
   corrected version. Limitation disclosed (the conversion helper modeled 1:1; the bug proven is purely the branch
   ordering, which is faithful to source).

## Mocks
- `MockPositionNFTs` — `FEE_MANAGER_NFT()` constant (only ctor-time read). (H-03)
- dummy non-zero addresses for aave/wiseLending/oracle/wiseSecurity (stored, not called on the bad-debt path). (H-03)
- H-04 needs no mocks (pure control-flow reproduction).

## State-inspection / invariant helpers
Public state on the real contracts is read directly: `totalBadDebtETH()`, `badDebtPosition(nftId)` (H-03). The PoCs
assert conservation/value-delta invariants (post-payback global == 0; uncollateralized receive == private % only).

## Limitations (honest)
- A **full** deposit→borrow→price-drop→liquidate→bad-debt runtime was **not** built — and the calibration shows it
  was **not needed** to prove these two exact mechanisms (they are localized accounting asymmetries). For mechanisms
  that genuinely require cross-contract state evolution (e.g. interest accrual + oracle drift driving the liquidation
  threshold), Tier A would still be required; that depth is future work.
- H-04 is Tier C (faithful reproduction), not the deployed private function. Strong, but one notch below H-03's
  real-production-code Tier B.
