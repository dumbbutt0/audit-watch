# kleidi-2024-10-holdout — SCORECARD

Freeze hash: 435dff55bbcf0c915399dc96b60e10ac6e3d12906aa098433be44046bbe848fe (before reveal).
Sealed-key hash: 1deef6f39536eb73. Awarded: 0 High + 3 Medium = 3 (hardened, Solidity-Labs-authored).

## Awarded-finding scoring
| Awarded | Sev | My candidate | Class | Credit |
|---|---|---|---|---|
| M-01 gas griefing via creating proposals (live-proposal set / pause loop) | Medium | — | MISSED | 0 |
| M-02 wrong handling of calldata-check indices → spurious reverts | Medium | K-M2/K-M3 (flagged calldata-check index logic + removal corruption as fragile, not the exact revert) | SAME_AREA_WRONG_MECHANISM | 0.25 |
| M-03 updateExpirationPeriod blocked when newPeriod < currentPeriod | Medium | — | MISSED | 0 |

## System-finding scoring (precision)
K-M2/K-M3→PLAUSIBLE (calldata-index area, partial M-02); K-M1 (recoveryThreshold==0 footgun)→PLAUSIBLE
(not awarded); K-L1/K-L2→BENIGN; create_time lens 2 candidates (create/deploy flow)→BENIGN (advisory,
not real — no receiver-callback-before-state-commit exploit). Hard false positives submitted as High: 0.

## Metrics
- High recall: n/a (0 Highs awarded).
- Medium recall: strict 0/3 = 0%; credited 0.25/3 = 8%.
- Weighted recall (denom 3): numerator 0.25 → **8.3%**.
- Precision: 0 FP-as-High; advisory create-time lens produced 2 benign (advisory noise, routing_allowed=False).
- Coverage: 100% in-scope read (64/64 critical). Gate PASS.
- Advisory lens contribution to recall: 0 (safe-mgmt 0 on a real Guard; create-time 2 benign).
- Proof: BLOCKED_BY_BUILD.

## Miss attribution
- M-01 → **Reasoning depth** (unbounded live-proposal griefing / DoS; read but not reasoned)
- M-03 → **Reasoning depth** (subtle expiration-update ordering logic)
(M-02 partially credited; residual → Reasoning depth.)

## Note
Honest hardened-target datapoint: a formally-reasoned wallet with only subtle Medium logic/DoS bugs; the
frozen system recovered ~8% weighted. Training-data confound minimal here (low-profile findings).
