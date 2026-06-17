# P288 — REVEAL_AND_SCORE (ecg-2023-12, opened AFTER pre-reveal freeze)

Answer key opened only after `outputs/pre_reveal_freeze.json`. Awarded H/M = 29 (4H/25M). Data:
`outputs/reveal_score.json`. (Only the 4 Highs + the Mediums on surfaced loci were enumerated — content-light.)

## Awarded Highs through the funnel
| id | awarded locus | exact function surfaced? | queued | READY | PoC | match level |
|---|---|---|---|---|---|---|
| H-01 | ProfitManager.claimGaugeRewards | area only (claimRewards surfaced) | ✓ | ✗ | ✗ | SUBSYSTEM_ONLY_RECALL |
| H-02 | ERC20RebaseDistributor.transfer | contract only (_burn/distribute) | ✓ | ✗ | ✗ | SUBSYSTEM_ONLY_RECALL |
| **H-03** | **LendingTerm.onBid** | **EXACT** | ✓ | ✗ (INLINE_GUARD_REFUTED) | ✗ | SAME_AREA_WRONG_MECHANISM |
| **H-04** | **SurplusGuildMinter.stake** | **EXACT** | ✓ | ✗ (NEEDS_VALUE_FLOW) | ✗ | SUBSYSTEM_ONLY_RECALL |
| M-02 | RateLimitedMinter.mint | EXACT (advisory, not queued) | ✗ | ✗ | ✗ | SUBSYSTEM_ONLY_RECALL |
| M-03 | ProfitManager.totalBorrowedCredit | area only | ✗ | ✗ | ✗ | MISSED |

## Reading
- **Locus recall is strong**: all 4 High *contracts* surfaced; **2/4 exact High functions surfaced AND queued**
  (LendingTerm.onBid = H-03, SurplusGuildMinter.stake = H-04); even M-02's exact function (RateLimitedMinter.mint)
  surfaced as an advisory candidate.
- **But 0 reached READY and 0 STRONG/EXACT mechanism recovery.** The exact-locus Highs stalled:
  - **H-04 stake**: surfaced+queued → NEEDS_VALUE_FLOW_EVIDENCE. The awarded mechanism — *immediate slash when staking
    into a gauge that previously incurred a loss* — is a loss-accounting/state-coupling bug; no current lens
    (anomaly/sibling/registry/rounding/oracle) derives it → NO_REFERENCE.
  - **H-03 onBid**: surfaced+queued → INLINE_GUARD_REFUTED. The awarded mechanism — *bad-debt cascade across auctioned
    loans* — is an accounting-contagion bug, not an access issue; the gate read the function's guard and (correctly for
    access, wrongly for this bug class) refuted it. SAME_AREA_WRONG_MECHANISM.
- **0 false positives, 0 false READY, severe FP=0.** The pipeline stayed precise; it produced no spurious finding.

## Pre-reveal candidate classification
All 8 validation candidates were BENIGN/INCONCLUSIVE pre-reveal (none claimed READY). No NONAWARDED_TRUE_POSITIVE; no
FALSE_POSITIVE. The two exact-awarded loci (stake, onBid) are recall hits whose mechanisms the evidence layer did not
derive.
