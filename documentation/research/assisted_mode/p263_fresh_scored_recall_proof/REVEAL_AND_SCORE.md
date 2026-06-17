# P263 — REVEAL_AND_SCORE (benddao findings; FULL per-issue; POST-FREEZE)
## Freeze integrity (recorded BEFORE opening findings)
BASE_FREEZE b7e8b0fc… · PRIORITIZER 2538c007… · RECALL_SWEEP 29459529… · SELECTED_LOCI 12e67226… ·
RANKING 0b5bcb90… · PROCEDURE 15833413… · recall_sweep.json aea8d04f…. Reveal source: cloned
code-423n4/2024-07-benddao-findings (PUBLIC) post-freeze. Awarded: 8 High + 20 Medium.

## The narrow-baseline vs recall-delta fact (decisive)
Narrow top-5 baseline (old pre-P262 path) = {_repayUserERC20Debt, executeCrossLiquidateERC721,
calculateUserAccountDataForLiquidate, updateInterestIndexs, validateDepositERC721} — **100% liquidation/interest/
deposit; ZERO yield-staking loci.** The recall sweep forced the **yield-staking subsystem** (YieldStakingBase
batchStake/batchUnstake/batchRepay) IN as RECALL-DELTA.

## Award-class of the 8 Highs (full per-issue)
| H | title (area) | award-class | recall status |
|---|---|---|---|
| H-01 | yield shares/assets mismatch (YieldStakingBase) | subtle_accounting_state | **FORCED_BY_RECALL_SWEEP** (yield; narrow skips); SL1-adjacent (stake vs my unstake), mechanism T8 not my T5 → FORCED_BUT_MECH_PARTIAL |
| H-02 | isolateRepay missing onBehalf==nftOwner | access_control | out-of-class |
| H-03 | missing clear lockerAddr | state/access | out-of-class |
| H-04 | underflow locks liquidated NFT | mechanical_math | (T9-ish) not selected |
| H-05 | bad debt never handled (insolvency) | subtle_accounting_state (T7) | **FORCED_BY_RECALL_SWEEP** (GenericLogic.calculateUserAccountData, recall-delta); FORCED_BUT_NOT_SELECTED |
| H-06 | yield unstake incompatible (Etherfi) | subtle (yield) | **FORCED_BY_RECALL_SWEEP** (yield); FORCED_BUT_MECH_PARTIAL |
| H-07 | auction NFT w/o bidding, missing msg.sender | access_control | out-of-class |
| H-08 | bot can't unstake/repay risky yield positions | subtle (yield liveness, T5) | **FORCED_BY_RECALL_SWEEP + SELECTED(SL1) + T5-family-match + PARTIAL_CHAIN pre-reveal** ✅ |

## Per selected-locus scoring
- **SL1 yield unstake/repay (RECALL-DELTA):** awarded **H-08** (bot can't unstake/repay risky positions) →
  **FORCED_BY_RECALL_SWEEP** (yield subsystem outside narrow top-5) + SELECTED + my C-winner **T5 liveness**
  ("unstake/repay partial-fill strands position") **family-matches** H-08 + PROCEDURE PARTIAL_CHAIN pre-reveal.
  Honest precision: family-level (I did not pin H-08's exact bot-DoS root cause); also H-01/H-06 (yield Highs) sit
  on this subsystem but on adjacent fns (stake/Etherfi-unstake) / different mechanism (T8 shares) → FORCED_BUT_MECH_PARTIAL.
- **SL3 crossLiquidateERC20 (RECALL-DELTA):** awarded **M-13** "no max liquidation price → insolvency" in
  executeCrossLiquidateERC721 (cross-liq subsystem) → my B-winner **T7 solvency-boundary over-seize** family-matches;
  but M-13's exact fn (executeCrossLiquidateERC721) is narrow-baseline #2 → ENUMERATED, area-match, partial recall-delta credit.
- **SL2 _accrueFeeToTreasury (RECALL-DELTA):** no clean exact award; interest/fee Mediums (M-18 fee factor, M-19
  rate-model) are nearby → SAME_AREA, NOT a clean recovery.
- **SL4 _repayUserERC20Debt (narrow):** repay-related award is H-02 (access_control, isolateRepay) → out-of-class; no recovery.

## FP / guard
Recall sweep = advisory, 0 concluded/severity/reportable (asserted). Manual B/C+5ops emitted only PARTIAL_CHAIN
hypotheses — **0 severe concluded/reportable FP**.

## Recall-delta credit (the P262 win condition)
≥1 fresh AWARDED locus FORCED into discovery that the narrow baseline would skip: **YES** — the entire yield-staking
subsystem (H-01/H-06/H-08 Highs + M-06/07/15/16) was zero-represented in narrow top-5 and forced in by the sweep;
SL1 selected it and reached a PARTIAL_CHAIN family-matching awarded **H-08**. Plus H-05 (bad-debt insolvency, T7)
forced in as recall-delta (not selected).
