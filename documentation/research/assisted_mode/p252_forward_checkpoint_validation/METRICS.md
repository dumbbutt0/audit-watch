# P252 — Metrics

salty-2024-01, controlled A/B. Awarded denom: 6H + 31M (37); weighted = 6·3 + 31 = 49. Both arms operated on
the read state-transition core (P245 enabled identically in both → coverage not an A/B confound).

## Candidate birth
| arm | candidates | (state-core loci engaged) |
|---|---|---|
| Arm A (baseline) | 5 (SA-1..SA-5) | castVote, Staking, StakingRewards |
| Arm B (+checkpoints) | 6 (SA-1..SA-5 + CP-1) | + DAO finalize/execute (CP-1) |
**candidate_birth_rate:** Arm B > Arm A by **+1 new candidate** (CP-1), born at a locus Arm A skimmed. The
checkpoints also fired (asked questions) at the H-02/H-04/M-01 loci, but those did not yield constructed
candidates pre-reveal.

## Exploit chains
| arm | completed chains |
|---|---|
| Arm A | M-06/M-11 (vote-staleness, SA-1) ; M-01 partial |
| Arm B | same + CP-1 (non-awarded) |
**exploit_chain_completion_rate:** no awarded chain was completed by a checkpoint that base hadn't already
completed. CP-1 added one (non-awarded) completed chain.

## Checkpoint activity
| checkpoint | records | candidates created | advanced (awarded-equiv) | rejected/benign |
|---|---|---|---|---|
| accounting | 91 | 0 new (reinforced SA-3/SA-5) | 0 | ~91 |
| state-transition | 20 | 1 (CP-1) + reinforced SA-1 | 0 | ~18 |
**candidate_per_checkpoint_record:** 1 / 111 ≈ **0.009** (1 new candidate from 111 question-records).

## Recall (per arm)
| arm | raw High recall | weighted recall |
|---|---|---|
| Arm A | 0/6 = 0% | M-06+M-11 (2×1) + M-01(0.5) = 2.5 / 49 = **5.1%** |
| Arm B | 0/6 = 0% | same 2.5 / 49 = **5.1%** (CP-1 non-awarded adds 0) |
**Recall lift (Arm B − Arm A): 0.0 weighted, 0 High.** (Absolute recall is low because 34/37 awards are
outside the read state-core or are reasoning-deep — coverage + reasoning bound; salty is heavily audited.)

## Marginal contribution (the primary table — see CONTRIBUTION_ANALYSIS.md)
CHECKPOINT_ONLY awarded = **0** · genuine BASE_PLUS_CHECKPOINT = **0** · BASE_ONLY = 3 · MISSED = 34.

## Noise / FP
Checkpoints emit **0 findings, 0 severity, 0 conclusions** (re-verified). Arm B added 1 non-awarded candidate
(CP-1) + 1 low (CP-3) over Arm A → FP-by-candidate +2 (gated candidates, not findings); not material. No
unrelated review explosion.

## Question burden
111 question-records (accounting 91 + state-transition 20) → 1 new candidate. candidate-per-question ≈ **0.009**.
Answering ≈ tens of minutes. Burden reasonable but **yield-per-question is very low on this contest**.
