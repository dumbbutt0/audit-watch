# P271 — SETUP (Lending Runtime Scaffold — CALIBRATION)

**RESEARCH-ONLY · CALIBRATION BUILD, NOT a blind scored recovery.** P271 is explicitly allowed to use the Wise
H-03/H-04 reveal (already opened in P270) because its purpose is to learn how to turn *"right awarded locus/family"*
into *"exact mechanism + runtime proof"* for lending systems. **No fresh-recovery claim is made.** It does NOT touch
recall / P260 / P262 / P264 / P267 selector / P269 triage / dashboard / scoring.

## The P270 bottleneck this fixes
P270 routed onto the exact loci of two Wise awarded Highs (H-03 FeeManager bad-debt; H-04 WiseCore liquidation
collateral misallocation) but stayed **family-level** because the confirming PoC needs the heavy lending runtime.
P271 builds a reusable lending runtime scaffold + sharpens both to **exact mechanism + runtime PoC**.

## Calibration cases (post-reveal)
- **H-03** — `WiseSecurity.checkBadDebtLiquidation` → `FeeManager.increaseTotalBadDebtLiquidation` (`_increaseTotalBadDebt`:
  `totalBadDebtETH += diff`) + `setBadDebtUserLiquidation` (`_setBadDebtPosition`: `badDebtPosition[nftId] = diff`, an
  **overwrite, not increment**). Across multiple partial liquidations the global accumulates while the position holds
  only the latest → payback removes only the latest → "fake debt" stuck in `totalBadDebtETH` → bricks
  `claimFeesBeneficial`/`claimWiseFees` (which gate on `totalBadDebtETH == 0`).
- **H-04** — `WiseCore._calculateReceiveAmount`: `potentialPureExtraCashout` is sized from the position's **normal
  deposit shares** (`userLendingData[...].shares × _removePercentage`) and paid out **before** the
  `unCollateralized == true` early-return (line 592) → a liquidator of an uncollateralized position extracts extra
  collateral beyond the private-collateral percentage. Fix = early-return on uncollateralized right after pure-
  collateral processing.

## Project / toolchain (reused from P270, isolated)
`pocs/p271/wise/`: Wise `contracts/` copied read-only to `wise_src/`; deps `lib/` (forge-std v1.9.6, OZ v4.9.6);
`foundry.toml` (solc 0.8.24, evm shanghai, `contracts/=wise_src/` remap, skip `@pendle` oracle libs + contest `.t.sol`).
Contest source unmodified.

## Frozen baselines (verified; must stay byte-identical — not touched)
P260 `d6b494bc` · P262 `a48336275f` · P264 `85f9cbe6` · P267 `b0623b8c` · P269 `63c88d02` (+ configs). Forbidden 5:
dashboard_sync `c1af70e1` · deep_trace `c095c426` · min_confirm_gate `2a15169a` · confirm_gate `afc481c9` ·
validate_p208 `ae55eb80`. Active audit `output → audits/size-credit-2024-06-blind/output`.

## Safety
No production authority / auto-submission / severity / reportable / submission-ready / confirmed. Calibration-not-fresh
stated in every doc. No production-source edits; contest source only copied read-only into `pocs/p271/`.
