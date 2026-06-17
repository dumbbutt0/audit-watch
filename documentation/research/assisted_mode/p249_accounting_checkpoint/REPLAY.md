# P249 — Part C: Replay (the 5 P248 accounting misses)

Ran `accounting_checkpoint_audit.py` on the three contests holding the 5 accounting misses (via `--manifest`,
no audit switch). For each miss: did the checkpoint OBSERVE the locus + family? Then the operator answers the
six questions → constructed candidate + exploit chain. **Before** = the P246 frozen-hunt result; **After** =
with the checkpoint's questions applied at the locus. Outputs: `outputs/<contest>_checkpoint.json`.

## Observation (checkpoint fired at every miss locus)
| Miss | Locus | Family observed | Observed? |
|---|---|---|---|
| kleidi M-02 | BytesHelper.sliceBytes / Timelock._addCalldataCheck | A5 | ✅ |
| centrifuge M-05 | InvestmentManager._deposit / processDeposit | A4 | ✅ |
| centrifuge M-07 | InvestmentManager._calculateTrancheTokenAmount | A1 | ✅ |
| munchables M-03 | LockManager._lock | A3 | ✅ |
| munchables M-04 | LockManager.setLockDuration | A5* | ✅ |
*M-04's defect is an *omitted* `forceHarvest`, so no positive A2/A3 marker can match; the checkpoint still
caught the locus via its A5 arithmetic shape, and the six universal questions (esp. Q2/Q6) reach the issue.

## Constructed candidates (operator answers the six questions → exploit_hypothesis + chain)
- **kleidi M-02 (A5).** Q-index-exactness: `length = end − start` (no `+1`). Hypothesis: a parameter that
  fills all its bytes makes `getSlicedBytesHash` length wrong → `checkCalldata` reverts. **Chain:** craft a
  whitelisted calldata whose checked param is full-width → hot-signer call reverts spuriously → legitimate
  whitelisted action permanently blocked. Candidate ✅ Chain ✅
- **centrifuge M-05 (A4).** Q4 (another actor deprived?): `_deposit` pulls tranche shares from the *shared*
  escrow on behalf of one user. Hypothesis: a user claiming via `deposit()` draws down shared escrow shares.
  **Chain:** user A `deposit()` empties escrow shares → users B…N cannot claim their maxDeposit/maxMint →
  starvation. Candidate ✅ Chain ✅
- **centrifuge M-07 (A1).** Q5 (rounding wrong side?): `_calculateTrancheTokenAmount` uses `Rounding.Down` on
  a withdraw path. Hypothesis: EIP-4626 requires rounding toward the vault (UP) on withdraw. **Chain:**
  repeated withdraws round in the user's favor → cumulative value leak / integrator mis-assumption.
  Candidate ✅ Chain ✅
- **munchables M-03 (A3).** Q3 (counted twice?): `_lock` does `quantity = _quantity + remainder` then carries
  `remainder` forward. Hypothesis: the stored remainder is re-added in subsequent locks and re-counted for
  NFTs. **Chain:** split locks to accumulate remainder → extra Munchable NFTs minted for free. Candidate ✅
  Chain ✅
- **munchables M-04 (A5 locus + Q2/Q6).** Q2 (value destroyed?) / Q6 (repeat amplify?): `setLockDuration`
  changes the lock without a pre-`forceHarvest` (unlike `lock`/`unlock`). Hypothesis: pending schnibbles
  rewards are computed against the new duration → reward accounting corrupted. **Chain:** call
  `setLockDuration` before harvest → rewards mis-credited/lost. Candidate ✅ Chain ✅

## Before → After
| Miss | Before: candidate? | Before: chain? | After: candidate? | After: chain? |
|---|---|---|---|---|
| kleidi M-02 | partial (fragility noted) | ✗ | ✅ | ✅ |
| centrifuge M-05 | partial (accounting noted) | ✗ | ✅ | ✅ |
| centrifuge M-07 | partial (rounding noted) | ✗ | ✅ | ✅ |
| munchables M-03 | partial (remainder, wrong direction) | ✗ | ✅ | ✅ |
| munchables M-04 | ✗ (read, missed) | ✗ | ✅ | ✅ |
| **Totals** | 0/5 full candidates, 0/5 chains | | **5/5 candidates** | **5/5 chains** |

## Result vs success criteria
- ≥4/5 misses become candidates → **5/5** ✅
- ≥3/5 produce exploit chains → **5/5** ✅
(0 FP and unrelated-volume in Part D.) The checkpoint's six questions, applied at the observed locus, are what
turn each P246 partial/miss into a constructed candidate + chain — without the checkpoint concluding anything.

## Honest caveats
- These chains are reconstructed by the operator answering the checkpoint's questions; correctness is
  confirmed against the P247/P248 ground truth → the standing training-confound caveat applies (a truly-unseen
  contest may not yield the answer as readily). The checkpoint guarantees the *question is asked at the locus*,
  not that the answer is found.
- M-04's family label (A5) is imperfect (its defect is an omission); the locus + universal questions still
  carry it.
