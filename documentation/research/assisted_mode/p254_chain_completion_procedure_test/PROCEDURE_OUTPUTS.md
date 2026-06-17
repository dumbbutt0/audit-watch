# P254 — Phase 3: Manual five-operation routine per locus (PRE-REVEAL, FROZEN)

Each locus: all five operations (STS / AAS / TSE / IDC / CCIT) performed by hand, each labelled
`PASS` / `NO_EFFECT` / `UNCLEAR` / `CANDIDATE_STRENGTHENED`, then a final chain status
`COMPLETED_CHAIN` / `PARTIAL_CHAIN` / `NO_CHAIN` / `REFUTED`. Written before the sealed key was opened.
Honesty rule: where an operation could not complete blind, it is labelled `UNCLEAR`/`NO_EFFECT` — not forced.

---
## L1 — `AuraVault.claim` (base B-2)  →  **PARTIAL_CHAIN**
- **STS — PASS.** Pre: vault holds earned BAL/AURA in rewardPool. Action `claim(amounts, maxAmountIn)`:
  `getReward()` pulls earned in; `amountIn` (asset) computed from **caller's** `amounts` via oracle; pulls
  `amountIn` from caller; re-deposits; transfers `amounts[0]` BAL + `amounts[1]` AURA to `msg.sender` and
  `amounts[i]*lockerIncentive/BASIS` to `lockerRewards`. Post: caller paid `amountIn` asset, received
  `amounts` tokens. Repetition: callable each block; bounded only by the vault's BAL/AURA *balance*, not by earned.
- **AAS — CANDIDATE_STRENGTHENED.** Attacker (any EOA) chooses `amounts[]` freely. Nothing ties `amounts` to
  `earned()`. So the attacker sets `amounts[0]` up to the **entire** vault BAL balance (incl. previously
  accumulated, not just newly earned) and likewise AURA — converting at oracle price **minus `claimerIncentive`**.
- **TSE — PASS.** Terminal: vault BAL/AURA balance can be pushed to ~0 (paid out to caller + lockerRewards) in
  exchange for `amountIn` asset; the extra `amounts*lockerIncentive/BASIS` to lockerRewards is paid **on top of**
  earned each call → vault under-collateralised on reward tokens vs shares.
- **IDC — CANDIDATE_STRENGTHENED.** Conserved invariant *should* be: vault only distributes rewards actually
  earned, and claimers pay fair value. Delta: vault loses `claimerIncentive` fraction on the **whole** balance
  (not just earned) **plus** a `lockerIncentive` over-payment per call. Loser = vault shareholders; gainer =
  claimer + lockerRewards. Amplifiable by repeated calls / sandwiching the oracle.
- **CCIT — NO_EFFECT.** Single contract; one `msg.sender`.
- **Chain status: PARTIAL_CHAIN.** Routine moved B-2 from "amounts unvalidated" → "attacker converts the full
  reward-token balance at an incentive discount + forces locker over-payment." Quantified *clean* drain still
  depends on oracle/param values (left honest as partial). **Completing ops: AAS + IDC.**

## L2 — `CDPVault.liquidatePosition` (base B-4)  →  **PARTIAL_CHAIN**
- **STS — PASS.** Pre: position barely unsafe (debt ≈ collateral·spot/liqRatio). Action: liquidator picks
  `repayAmount`; `takeCollateral = repayAmount/discountedPrice` (discountedPrice = spot·liqDiscount < spot);
  `deltaDebt = repayAmount·liqPenalty`; debt reduced by `deltaDebt` (via `calcDecrease`). Post: collateral
  removed = `repayAmount/discountedPrice` (value ≈ `repayAmount/liqDiscount` > repayAmount); debt removed =
  `repayAmount·liqPenalty` < repayAmount. Repetition: no post-liquidation safety/health-improvement check →
  repeat with dust `repayAmount`.
- **AAS — PASS.** Any EOA liquidator; `repayAmount` fully attacker-chosen; only precondition is the position is
  unsafe at entry.
- **TSE — PASS.** Each round removes more collateral *value* than debt relieved → collateralisation
  monotonically **worsens**; terminal state = position driven into bad debt that `liquidatePositionBadDebt`
  then socialises as `loss` to the pool.
- **IDC — CANDIDATE_STRENGTHENED.** Invariant *should* be: liquidation does not reduce a position's health.
  Delta per round = collateral-out (`repayAmount/liqDiscount`) − debt-down (`repayAmount·liqPenalty`) > 0 against
  the borrower; the discount is pure liquidator profit even on a position needing only a small top-up. Loser =
  borrower (and pool, via induced bad debt); gainer = liquidator.
- **CCIT — NO_EFFECT.** Identity not the issue here.
- **Chain status: PARTIAL_CHAIN.** Routine moved B-4 from "penalty/deltaDebt asymmetry" → "partial liquidation
  is not gated on health improvement; discounted-collateral seizure lets a liquidator extract the discount and
  push a marginally-unsafe position to bad debt." **Completing ops: IDC + STS.**

## L3 — `SwapAction.swap` + `PositionAction` residual recipient (base B-5)  →  **REFUTED (NO_CHAIN)**
- **STS — NO_EFFECT.** No persistent state transition; per-call token routing.
- **AAS — UNCLEAR.** Attacker can set `recipient`/`residualRecipient` to themselves and skip recipient
  validation in some paths (`_borrow` auxSwap unchecked; raw `swap` EXACT_OUT leftover → `swapParams.recipient`).
- **TSE — PASS (benign).** Residual `limit − retAmount` and `pendleJoin` `balanceOf(this)` leave to the chosen recipient.
- **IDC — NO_EFFECT.** No net protocol-level conserved-value delta identified.
- **CCIT — PASS, but REFUTES.** Tracking principals: `PositionAction`/`SwapAction` execute via **delegatecall in
  the user's PRBProxy** (`address(this)` = the caller's own proxy), so the residual/`balanceOf` funds are the
  **caller's own**. The receiving principal (recipient) and the spending principal (the proxy owner) are the
  **same party** — no cross-principal mismatch, no victim. The identity check the routine performs *refutes* the
  candidate rather than completing it.
- **Chain status: REFUTED (NO_CHAIN).** Honest negative: the CCIT operation, performed properly, shows per-proxy
  isolation removes the victim. **Completing op: CCIT (refuting) — the routine did not hallucinate a chain.**

## L4 — `StakingLPEth.cooldownAssets/cooldownShares` (base B-1)  →  **PARTIAL_CHAIN**
- **STS — CANDIDATE_STRENGTHENED.** Pre: `cooldowns[u] = {cooldownEnd:T1, underlyingAmount:X}`. Action: u calls
  `cooldownAssets(Y)` again → `cooldownEnd = now + cooldownDuration (T2 > T1)`, `underlyingAmount = X+Y`. Post:
  the already-cooling `X` is re-locked until `T2`. Repetition: any new cooldown call indefinitely postpones the
  whole bucket's unlock. Edge: dripping small amounts ⇒ earlier funds never become claimable.
- **AAS — NO_EFFECT (REFUTES escalation).** Both functions key off `msg.sender` only; **no on-behalf/identity
  parameter**, so an attacker **cannot** force another user's cooldown reset. Self-inflicted only → caps severity.
- **TSE — PASS.** Funds are **delayed, not lost** — recoverable after `T2`, or via `unstake` once owner sets
  `cooldownDuration = 0`. Not stranded permanently.
- **IDC — NO_EFFECT.** No value created/destroyed; only timing.
- **CCIT — NO_EFFECT.**
- **Chain status: PARTIAL_CHAIN.** Routine completed the *mechanism* (re-cool resets the whole bucket's timer)
  but AAS+TSE honestly **bound it down** to a self-inflicted timing/UX issue (Low/Medium), not a fund-loss High.
  **Completing op: STS (mechanism); AAS/TSE (severity bound).**

---
### Pre-reveal summary (frozen)
| locus | chain status | completing op(s) | blind severity |
|---|---|---|---|
| L1 AuraVault.claim | PARTIAL_CHAIN | AAS + IDC | High? (partial) |
| L2 CDPVault.liquidatePosition | PARTIAL_CHAIN | IDC + STS | High? (partial) |
| L3 SwapAction/PositionAction residual | REFUTED / NO_CHAIN | CCIT (refute) | — |
| L4 StakingLPEth cooldown | PARTIAL_CHAIN | STS (AAS/TSE bound down) | Low/Medium |

**0 COMPLETED_CHAIN (full-confidence), 3 PARTIAL_CHAIN, 1 REFUTED** — recorded before the key was opened.

**FREEZE:** final. Hashes of BASE_HUNT_FREEZE.md + SELECTED_LOCI.md + this file are computed and recorded in
REVEAL_AND_SCORE.md **before** `audits/loopfi-2024-07-holdout/reports/` is read.
