# P252 — Contribution Analysis (the mandatory primary output)

Per awarded finding: recovered? and by whom — BASE_ONLY / CHECKPOINT_ONLY / BASE_PLUS_CHECKPOINT / MISSED.
"Recovered" = an arm produced a candidate that is awarded-equivalent (direct or partial). CHECKPOINT_ONLY =
recovered only via an Arm-B candidate ABSENT from the frozen Arm A. Hindsight credit is forbidden: a checkpoint
gets credit only for what was actually constructed pre-reveal.

| Award ID | Severity | Recovered? | Recovered by |
|---|---|---|---|
| H-01 VestingWallet release access control | High | no | MISSED (out of read state-core) |
| H-02 first-LP claims all initial pool rewards | High | no | MISSED (checkpoint fired at `_increaseUserShare` but chain not constructed pre-reveal) |
| H-03 spot-price manipulation / liquidations | High | no | MISSED |
| H-04 first-depositor breaks staking-rewards accounting | High | no | MISSED (checkpoint fired at locus; not constructed) |
| H-05 evade liquidation via min-deposit cooldown reset | High | no | MISSED |
| H-06 repaid USDS to wrong address → bad debt | High | no | MISSED |
| M-01 excess rewards via virtualRewardsToRemove→0 | Med | partial | **BASE_ONLY** (SA-5 flagged the rounding locus; direction not completed) |
| M-06 reuse SALT from prior voting → malicious pass | Med | yes | **BASE_ONLY** (SA-1) |
| M-11 staker gains voting power by unstaking xSALT | Med | yes | **BASE_ONLY** (SA-1) |
| M-02 persistent call revert blocks finalization | Med | no | MISSED (CP-1 was the inverse skip-case, not this) |
| M-03/M-12/M-13/M-14/M-19 proposal DOS / lifecycle | Med | no | MISSED (SA-4 weak-area only) |
| M-23/M-10/M-20/M-24 reward-share / arbitrage rewards | Med | no | MISSED (SA-3 area only) |
| M-04,M-05,M-07,M-08,M-09,M-15–M-18,M-21,M-22,M-25–M-31 | Med | no | MISSED (oracle/liquidation/POL/wallets/zap — out of read-scope) |

## Tally
| Class | awarded count | which |
|---|---|---|
| **CHECKPOINT_ONLY** | **0** | — (the only NEW Arm-B candidate, CP-1, is not awarded) |
| **BASE_PLUS_CHECKPOINT** (genuine: checkpoint created/completed) | **0** | — (castVote/rewards reinforcements were redundant; no partial completed pre-reveal) |
| **BASE_ONLY** | 3 (2 Med direct + 1 Med partial) | M-06, M-11 (SA-1); M-01 partial (SA-5) |
| **MISSED** | 34 | the rest (coverage-bound + reasoning-bound) |

## The decisive numbers (per the phase's honesty rule)
- Awarded-equivalent findings that exist **only because of a checkpoint**: **0**.
- Awarded-equivalent chains the checkpoint **materially created or completed**: **0**.
- New candidates the checkpoint birthed: **1** (CP-1) — real but non-awarded.
- Checkpoints fired on the correct awarded loci (castVote, _increaseUserShare, _decreaseUserShare, DAO
  finalize) — observation worked — but did not convert to awarded chains pre-reveal.
