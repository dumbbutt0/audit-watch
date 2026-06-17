# P289 — LOSS_REWARD_LENS_DESIGN

## P288 diagnosis (the repair map)
ECG surfaced 2/4 exact awarded High functions (SurplusGuildMinter.stake H-04, LendingTerm.onBid H-03) and all 4 High
contracts, but produced 0 READY: every value candidate was `value_flow_present_but_no_anomaly` + invariant_delta
NO_REFERENCE. The missing mechanism families: loss/slash-on-stake · bad-debt contagion · reward-index init ·
share-transfer reward theft. P289 adds a lens per family. ECG bodies were read to GROUND the signal sets (supervised
eval); **no ECG function name or constant is used as a runtime signal** (a renamed-function fixture must still match).

## Common rules
All lenses run on the comment-stripped, lowercased body; require CONCRETE multi-signal state-coupling (verb + state-term
+ a per-user/global write), never naming alone; are fail-closed on ambiguity; emit `lens_name`, `lens_status`
(LENS_MATCH/LENS_PARTIAL/LENS_NO_MATCH/LENS_REFUTED), source_basis, attacker_path, affected_variables,
expected_invariant, broken_invariant_hypothesis, impact_delta, victim_gainer, poc_assertion, confidence (MEDIUM ceiling —
these are coupling heuristics, not exact anomalies), unresolved_assumptions, refutation_basis. Only LENS_MATCH at
HIGH|MEDIUM lifts (and only when class is value/state, attacker/impact/victim ≥MEDIUM, D1 doesn't refute).

## Lens 1 — loss/slash-on-stake coupling
MATCH when: a stake/deposit/join/enter verb + a loss/slash/deficit/badDebt/gaugeLoss state term + a per-user stake/share
write co-occur, AND the loss protection is missing OR INCOMPLETE (a same-block-only guard `!= block.timestamp` near a
loss term — protects only same-block loss, not prior-block). REFUTE when a user index/checkpoint is initialized to a
current global getter AND a prior-loss exclusion (pro-rate-after-stake) is present with no same-block-only narrowing.
NO_MATCH when no loss term or no stake write. (Anchor shape: SurplusGuildMinter.stake — init present but only
same-block loss guard → MATCH via the incomplete-guard rule.)

## Lens 2 — bad-debt/loss contagion
MATCH when: a loss event verb (bid/liquidat/auction/writeoff/repay) + badDebt/loss/deficit + a write to a GLOBAL/shared
accumulator (totalX / global / shared) with no per-term/per-position key on that write. REFUTE when all loss writes are
per-term/user-keyed (`[term]`/`[position]`/`[user]`), shared-risk is explicit, or admin-only/guarded. NO_MATCH when no
global loss write.

## Lens 3 — reward-index initialization
MATCH when: a rewardIndex/globalIndex/accumulator/checkpoint term + a per-user index term (userIndex/
userRewardPerTokenPaid/userCheckpoint) + a balance/stake/mint write, AND a claim/earned/accrue path exists, AND the user
balance becomes positive without the user index assigned from the current global in the same body. REFUTE when the
balance-write and user-index-write are atomic (both present in the body), or a helper resolved by trace initializes it,
or pre-balance periods are excluded. NO_MATCH when no per-user index term (e.g. a benign loop like
ProfitManager.claimRewards → NO_MATCH).

## Lens 4 — share-transfer reward theft
MATCH when: a transfer/transferFrom/_before/_afterTokenTransfer + shares/balance + reward/index/checkpoint + a
balance-dependent reward computation, AND no sender+recipient checkpoint update around the transfer. REFUTE when the
transfer path updates BOTH from and to checkpoints/shares (anchor: ERC20RebaseDistributor.transfer materializes both →
likely REFUTE/PARTIAL), token is non-transferable, or rewards are balance-independent. NO_MATCH when no reward/index
term.

## Confidence model & FP risks
Confidence MEDIUM max (coupling heuristic). The dominant FP risk is firing on benign stake/transfer/reward functions →
mitigated by multi-signal requirement + refutation conditions + the existing value/state-class + D1 + core-dim gates +
the supervised corpus FP check (severe FP must stay 0; any false READY in the audit → tighten or verdict C). The lenses
NEVER read award titles/bodies/IDs and use no ECG constants; signals are generic Solidity vocabulary.
