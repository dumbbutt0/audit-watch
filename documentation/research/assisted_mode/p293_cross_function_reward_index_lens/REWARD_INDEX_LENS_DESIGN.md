# P293 — REWARD_INDEX_LENS_DESIGN

## P292 diagnosis
P291 surfaced the awarded internal locus `StakingRewards._increaseUserShare`; P292 admitted it past the coverage
duplicate-class dedup so it reaches the gate. But the gate returned `NEEDS_VALUE_FLOW_EVIDENCE` because Lens 3
(`_lens_reward_index_init`, P289) returned `NO_REFERENCE`.

## Why span-local Lens 3 failed
`_lens_reward_index_init` required `global_idx AND user_idx AND bal_write AND reward_path` ALL in the candidate's own
body, matching only literal `rewardIndex/userIndex/...` names. Salty's reward mechanism is:
- global accumulator `totalRewards[poolID]`, per-user reward-debt `user.virtualRewards`, share `user.userShare` /
  `totalShares`, first-depositor branch `if (existingTotalShares != 0)` — **all non-standard names**, and
- the pending formula `userRewardForPool() = totalRewards*userShare/totalShares - virtualRewards` lives in a
  **same-contract sibling** (not the candidate, not a downward callee — the P283 trace from `_increaseUserShare`
  resolves nothing: its callees are `ceilDiv/dao/isWhitelisted/modificationCooldown`, all external/library).

So the miss was TWO things at once: naming (virtualRewards/totalRewards ≠ rewardIndex/userIndex) and cross-function
(the claim formula is a sibling).

## Cross-function trace use
`derive(item, manifest, audit_id, gate_evidence, trace_evidence)` already RECEIVES `trace_evidence` (built by the
P283 tracer in `completion_evidence_deriver`) but never used it. The new lens consumes it: it assembles the union of
(candidate body) + (resolved P283 trace callee bodies, re-resolved from the manifest by `build_index`) and, for the
pending formula, additionally scans bounded same-contract siblings (`_contract_functions`). Fail-closed: no trace +
no resolvable callee → span-local only; a candidate that needs an unreachable global → `LENS3_TRACE_UNRESOLVED`.

## Name-family approach (config-driven; generic; no target constants)
`lens3_user_share_terms` · `lens3_global_share_terms` · `lens3_global_index_terms` (incl. `totalrewards`,
`accrewardpershare`, `rewardpertoken`, `pointspershare`, `gaugeprofitindex`) · `lens3_user_index_terms` (incl.
`rewarddebt`, `paidindex`, `userrewardpertokenpaid`, `virtualrewards`) · `lens3_pending_terms` · `lens3_init_markers`.
Bare `index/reward/acc` are deliberately EXCLUDED (too broad) — global accumulator detection requires a specific term
(e.g. `total*reward*`).

## Five patterns
- **A MISSING_USER_INDEX_INIT** — share mutation + global index + NO per-user snapshot + a connectable ratio.
- **B SHARE_INCREASE_BEFORE_CHECKPOINT** — share write precedes the user checkpoint/updateReward call.
- **C GLOBAL_INDEX_NOT_PAIRED** — global accumulator + share update + a present-but-unpaired/stale user snapshot.
- **D FIRST_DEPOSITOR_ZERO_SUPPLY** — a `total*==0/!=0` branch conditionally skips the snapshot write (salty).
- **E LOSS_REWARD_INDEX_CONTAGION** — a global/shared loss accumulator coupled into a share mutation with no
  per-user exclusion (checked before the pending gate; loss propagation is itself the basis).

## Required evidence to LIFT (all)
(1) source-backed user share/stake/balance mutation, (2) source-backed global index/accumulator/reward/loss var,
(3) source-backed missing/stale/conditionally-skipped per-user snapshot, (4) the missing-init/ordering/zero-supply
deviation source-backed across the union, (5) a specific impact delta, (6) an implementable PoC assertion, (7) D1
inline guard does not refute (the gate enforces this — see `liquidateUser` below), (8) no unresolved assumption
carries the core claim. MEDIUM confidence ceiling. A `LENS3_READY` emits `invariant_delta_status =
REWARD_INDEX_INIT_FOUND` (already in config `lift_statuses`) so the gate lifts via config with no gate edit.

## False-positive controls
- **Relevance gate:** silent (returns `None`, leaving `derive()` unchanged) unless there is a per-user share write
  AND (global index OR user snapshot OR loss) — so non-reward candidates are never touched.
- **Refutation:** atomic init (user snapshot assigned from the current global) OR a checkpoint/updateReward CALL
  that PRECEDES the share write (the canonical Synthetix-correct ordering) → `LENS3_REFUTED_NORMAL_CHECKPOINT`.
- **Pending requirement:** A/B/C/D require a connectable pending/claim formula (in-span, callee, or sibling).
- **Loss contagion (E)** requires a *global/shared* loss accumulator (`(total|global|shared|gauge|cumulative)*loss`),
  not benign per-position loss.
- **Fail-closed blocks** (`LENS3_NO_GLOBAL_INDEX`, `LENS3_NO_USER_INDEX`, `LENS3_NO_ORDERING_EVIDENCE`,
  `LENS3_PATTERN_MATCH_HELD`, `LENS3_TRACE_UNRESOLVED`) keep `invariant_delta_status = NO_REFERENCE` (held) while
  surfacing a precise reason.
- **Gate-side D1** still independently refutes guarded paths (e.g. salty `liquidateUser` fires the lens but is held
  `INLINE_GUARD_REFUTED`).

## Examples that must NOT lift (verified)
- plain `_balances[msg.sender] += a;` (no global/reward) → silent.
- `updateReward(msg.sender); _balances[...] += a;` (checkpoint then mutate) → refuted.
- `userRewardPerTokenPaid[u] = rewardPerToken; balance += a;` (atomic init) → refuted.
- a guarded liquidation that touches reward accounting → lens fires but gate D1 holds it (not READY).
- every strict-eval target with no staking/reward subsystem (panoptic/silo/revert-lend/hybra) → 0 firings.
