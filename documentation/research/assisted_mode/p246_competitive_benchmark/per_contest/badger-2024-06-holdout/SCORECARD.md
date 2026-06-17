# badger-2024-06-holdout — SCORECARD

Freeze hash: cece6783189f903253e88a2b24b0b76a3a916adf2b94630f4e5e5ebff903a2b6 (before reveal).
Sealed-key hash: 05ee0ed459a96c16. Awarded: 0 High + 2 Medium = 2 (hardened, multiply-audited eBTC).

## Awarded-finding scoring
| Awarded | Sev | My candidate | Class | Credit |
|---|---|---|---|---|
| M-01 incorrect comparison logic in post-operation checks (BorrowerOperations/CdpManager) | Medium | — (not read) | MISSED | 0 |
| M-02 staking ETH incorrectly assumes revert bubbling | Medium | — (not read) | MISSED | 0 |

## System-finding scoring (precision)
B-M1 (Chainlink previous-round phase-boundary)→PLAUSIBLE (not awarded; eBTC oracle heavily reviewed);
B-M2 (adapter staleness defers to PriceFeed)→PLAUSIBLE. Hard FP: 0.

## Metrics
- High recall: n/a (0 Highs). Medium recall: 0/2 = 0%.
- Weighted recall (denom 2): numerator 0 → **0%**.
- Coverage completeness: ~1% (oracle layer only of 722 critical). **Gate BLOCKS** (coverage incomplete) —
  correct refusal on an oversized target.
- Advisory lens contribution: 0. Proof: BLOCKED_BY_BUILD.

## Miss attribution
- M-01 → **Coverage** (BorrowerOperations/CdpManager post-op checks unread)
- M-02 → **Coverage** (LeverageMacro/ActivePool staking path unread)

## Note
The deliberate large-target datapoint. With 722 critical items, full-coverage hunting in one pass is
infeasible; the P245 gate correctly BLOCKS triage. Recall is 0% — entirely coverage-bound. This is the
honest demonstration that the system does not scale to large targets in a single pass. (Both awarded bugs
are subtle Mediums in a codebase with many prior audits.)
