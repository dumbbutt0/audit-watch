# P252 — Arm A: Baseline (P245 only, NO checkpoints) — FROZEN pre-reveal

Genuine unaided hunt of the salty state-transition core (Staking, StakingRewards, SaltRewards, Proposals, DAO
skimmed). P245 gate: state-core read in full. No checkpoint used. This is frozen + hashed BEFORE any
checkpoint runs.

## Base candidates (Arm A)
| id | sev | locus | mechanism | chain? |
|---|---|---|---|---|
| SA-1 | Medium | Proposals.castVote | voting power is snapshotted at vote time and never re-validated at finalization; a voter can unstake (share decreases immediately) after voting and the recorded vote persists → stale/over-counted voting power can pass or block a ballot | partial (mechanism, not full exploit path) |
| SA-2 | Low/Med | Staking.calculateUnstake / recoverSALT | expedited-unstake fee + `numerator / (100*unstakeRange)` rounding; minor precision (favors protocol) | no |
| SA-3 | Low/Med | StakingRewards.addSALTRewards | permissionless reward donation → reward/share ratio frontrun (mitigated by emitter drip + cooldown per NatSpec) | partial |
| SA-4 | Low | Proposals._possiblyCreateProposal / markBallotAsFinalized | one-active-proposal-per-user; DAO confirmation bypasses; finalize clears proposer flag | no |
| SA-5 | Low/Med | StakingRewards._increaseUserShare / _decreaseUserShare | virtualRewards rounding (ceilDiv up on increase, div down on decrease) — protocol-favorable, user dust | no |

## Arm A summary
- Candidates: 5 (1 Med-flagship SA-1 + 4 Low/Med). Completed exploit chains: 0 full (SA-1/SA-3 partial).
- Honest note: salty is a heavily-audited, well-known protocol; this unaided base hunt is genuine but bounded.
  The flagship suspicion is the governance vote-power-staleness (SA-1).

FREEZE: Arm A candidates above are final, recorded BEFORE running the checkpoints.
