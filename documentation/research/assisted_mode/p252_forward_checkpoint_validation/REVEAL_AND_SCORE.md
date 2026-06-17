# P252 — Reveal & Score (post-freeze)

Freeze hashes (before reveal): Arm A `8810d7d6…`, Arm B `596aed4c…`. Answer key WEB-FETCHED from the Code4rena
Salty report AFTER both freezes. Awarded: **6 High + 31 Medium = 37** (sources below).

## Awarded findings my arms engaged (state-transition / reward core)
| Award | Sev | Description | Arm A had it? | Arm B add? |
|---|---|---|---|---|
| M-06 | Med | Reusing SALT from prior voting allows malicious proposals to pass | **yes — SA-1** | castpoint S3 reinforced (redundant) |
| M-11 | Med | SALT staker gains extra voting power by unstaking xSALT | **yes — SA-1** | castVote S3 reinforced (redundant) |
| M-01 | Med | Claim excess rewards via `virtualRewardsToRemove` rounding to zero (`_decreaseUserShare`) | partial — SA-5 (flagged the rounding, wrong direction/impact) | accounting A1/A3 reinforced; chain not completed pre-reveal |
| H-02 | High | First liquidity provider claims all initial pool rewards (`_increaseUserShare`) | no | accounting **fired at the locus** but I did NOT construct it pre-reveal |
| H-04 | High | First depositor breaks staking-rewards accounting (virtualRewards) | no | accounting fired at the locus; not constructed pre-reveal |
| M-23 | Med | StakingRewards pools receive incorrect reward share | no | accounting fired in area; not constructed |
| (33 others: oracle/liquidation/POL/arbitrage/upkeep/wallets…) | — | mostly outside the read state-core | no | n/a |

## My Arm-B-only candidate (CP-1) vs awards
CP-1 (DAO._executeApproval SEND_SALT skip-but-finalize) — **not an awarded finding** (the skip is the
intentional "prevent finalization revert" design per the NatSpec; M-02 is the *inverse* — a revert *blocking*
finalization). → CP-1 is a PLAUSIBLE non-awarded candidate, not awarded-equivalent.

## Honesty ruling on "did the checkpoint recover anything?"
The accounting checkpoint **fired exactly on the H-02/H-04/M-01 loci** (`_increaseUserShare`/`_decreaseUserShare`)
and the state-transition checkpoint fired on castVote (M-06/M-11) — the OBSERVATION step worked. But in the
**frozen** Arm B (pre-reveal) I constructed only CP-1 (non-awarded) and reinforced SA-1; I did **not** construct
H-02/H-04/M-01 from the checkpoint questions. Crediting them now would be hindsight contamination — forbidden.
So:
- **CHECKPOINT_ONLY awarded-equivalent recovered: 0** (CP-1 is not awarded).
- **Genuine BASE_PLUS_CHECKPOINT (checkpoint materially created/completed an awarded chain): 0** (the castVote/
  rewards reinforcements were redundant — base already had SA-1; the rewards chains were not completed
  pre-reveal).
- **BASE_ONLY awarded recoveries:** M-06 + M-11 (SA-1, vote staleness) [credited], M-01 (SA-5, partial).

## The key honest finding
The checkpoints **observe the right loci on unseen code** (castVote, _increaseUserShare/_decreaseUserShare,
DAO finalize — all real awarded-finding sites) and are FP-safe, but **observation did not convert into
awarded exploit chains** in this blind run: the binding constraint is *answering the question correctly*
(completing the chain), not *asking it at the right place*. This matches P250's caveat: the checkpoint
guarantees the question is asked at the locus, not that the answer is found on unseen code.

Sources: [Code4rena Salty report](https://code4rena.com/reports/2024-01-salty)
