# P252 — Arm B: Checkpoints (P245 + accounting + state-transition) — FROZEN pre-reveal

Arm A freeze hash: 8810d7d6b1422408bab812f033516395400c56af54550a39db9515e20f2afc65 (recorded before this).
Ran both checkpoints on the salty manifest. Invariant re-verified: both `emits_findings:false`,
`concludes_vulnerability:false`, **0 records carry a conclusion**. Checkpoint compute: **0.151 s**.
Question-records: accounting **91** (A4×35,A1×19,A3×19,A5×14,A2×4), state-transition **20** (S4×10,S3×7,S2×3).

## State-transition checkpoint hits on the governance/staking core
`Proposals.castVote` (S3), `Proposals.openBallots`/`openBallotsForTokenWhitelisting` (S2),
`DAO._finalizeApprovalBallot`/`_executeApproval` (S3), `DAO._finalizeParameterBallot`, `BootstrapBallot.finalizeBallot`.
The flag on `DAO._executeApproval`/`_finalizeApprovalBallot` pointed at a locus Arm A only **skimmed**.

## Arm B candidates = Arm A ∪ checkpoint-forced (tagged NEW / REINFORCED)
| id | sev | locus | source | NEW/REINF |
|---|---|---|---|---|
| SA-1..SA-5 | (carried) | (Arm A baseline) | base hunt | — |
| **CP-1** | Medium | DAO._executeApproval (SEND_SALT) | **state-transition S4** (answering Q6 "does a failure/shortfall branch still update state?") | **NEW** |
| CP-2 | Medium | Proposals.castVote (stale voting power) | state-transition S3 | REINFORCED (= SA-1) |
| CP-3 | Low | Proposals open-ballot EnumerableSets | state-transition S2 | NEW (low; bounded by 1-proposal/user) |
| CP-4 | Low/Med | StakingRewards reward/share pool (totalRewards) | accounting A4/A1/A3 | REINFORCED (= SA-3/SA-5) |

### CP-1 (NEW) — constructed candidate + chain
**Q6 (failure/shortfall branch still updates state?) at `DAO._executeApproval`:** for `SEND_SALT`,
`if (salt.balanceOf(this) >= ballot.number1) { transfer } ` — if the DAO balance is temporarily below the
approved amount, the transfer is **silently skipped**, yet `_finalizeApprovalBallot` then calls
`markBallotAsFinalized(ballotID)`. **Chain:** a passed SEND_SALT proposal whose amount momentarily exceeds the
DAO balance at finalization → ballot is consumed/finalized with the send never executed → the approved payout
is permanently lost and must be re-proposed (and `finalizeBallot` is permissionless, so anyone can finalize at
the unfavorable moment). State-transition: a shortfall branch finalizes state as if executed.

## Notes
- Accounting checkpoint (91 records) reinforced the Arm-A reward/rounding suspicions (SA-3/SA-5) but produced
  **0 NEW** candidates beyond Arm A on this contest.
- The marginal NEW contribution of Arm B is **CP-1** (state-transition S4 at the DAO finalize/execute locus
  Arm A skimmed), plus reinforcement of SA-1 (castVote staleness).

FREEZE: Arm B candidates above are final, recorded before reveal.
