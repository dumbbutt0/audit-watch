# Novelty / Public-Known Memo

**Status carried forward: `public_known_but_not_duplicate`. Clean novelty is NOT claimed.**

| Check | Result |
|---|---|
| Exact duplicate among awarded C4 2024-03 Abracadabra findings | **not found** (the LockingMultiRewards awards were M-05 lock-duration, M-07 reward-rate precision, M-14 native-token, M-15 gas-yield — none = expired-lock boost retention) |
| Contract publicly audited | **yes** (Code4rena 2024-03-abracadabra-money, public) |
| Design lineage public | **yes** — lock-boost + lazy `processExpiredLocks` expiry is the Convex `CvxLockerV2` / Curve MultiRewards pattern (NatSpec "Based from …") |
| Full raw issue set exhaustively reviewed | **no** — only the awarded/grouped report + report page were reviewed; ~200 raw submissions + the complete QA report were not line-by-line exhausted |
| Materially-equivalent issue found | **none located** |

## Honest position
No exact public duplicate was found, but the area is publicly audited and the underlying pattern is
public — so this is `public_known_but_not_duplicate`, **not** clean novelty. `novelty_clear` stays
**unknown/false**. A human should run an external Code4rena/KB + raw-issue check before asserting novelty in
any submission.
