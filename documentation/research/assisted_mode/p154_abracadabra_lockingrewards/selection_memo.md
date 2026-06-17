# P154 — Selection Memo

## Phase intent
Execute P153's **Option A**: point the conversion funnel at one fresh, deploy-light, unprivileged,
value-bearing holdout and either honestly reach `reportable_candidate_needs_human_review` or stop with a
precise blocker. Optimize for *conversion* (mechanism + reachability + severity + human-reviewable
evidence), not for `runtime_confirmed` alone.

## Shortlist (≥3), excluding the 6 used arches (noya/blackhole/centrifuge/velodrome/decent/ecg) and P150's
already-rejected vultisig & kelp

| id | audit | architecture | mechanism_class | surface_function | entrypoint | suspected value impact | deploy_complexity | reachability_precheck | corrected_ref | control | likely blocker | score reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **C1 (SELECTED)** | abracadabra-2024-03-holdout | staking / locking-rewards | boost-weight reward over-accrual | `earned`/`balanceOf` vs `processExpiredLocks` | `stake`/`lock`/`getRewards` (public, `whenNotPaused`) | reward tokens redirected from honest stakers | **light** (real contract + OZ Pausable + solmate Owned + solady SafeTransferLib + local MathLib/OperatableV2 + 2 ERC20 mocks) | answerable from source | feasible (process-promptly = real code) | feasible (active-lock window) | severity/scope (operator cadence) | best deploy-light + unprivileged + value-bearing + crisp |
| C2 | basin-2024-07-holdout | AMM (Well) | sibling fee-on-transfer parity | `swapFrom` vs `swapFromFeeOnTransfer` | public swap | mis-credited output | heavy (Aquifer clone + immutable args + Pump + WellFunction) | answerable | feasible | feasible | deploy_too_heavy | ideal shape, fails deploy-light |
| C3 | salty-2024-01-holdout | staking / batch rewards | batch-vs-single claim parity | `claimAllRewards(bytes32[])` | public batch | reward over/under-claim | moderate-heavy (3 config-interface mocks) | answerable | feasible | feasible | mocks-before-mechanism | strong shape, heavier mocks |
| C4 | pooltogether-2024-03-holdout | ERC4626 prize vault | rounding / yield-buffer | `deposit`/`withdraw`/`redeem` | public | share/asset mis-round | moderate (yield-source mock) | answerable | feasible | feasible | duplicate + intent | `claimPrize` is `onlyClaimer` (privileged); ERC4626 heavily audited |

## Why C1, and why the others were rejected
- **C2 rejected** — the Well's ideal sibling-parity shape is real, but it deploys via Aquifer clone +
  immutable-args encoding + a Pump + a WellFunction → violates the deploy-light criterion (criterion 8).
- **C3 rejected** — `claimAllRewards` is a clean batch path, but `StakingRewards` needs `IPoolsConfig`,
  `IExchangeConfig`, and `IStakingConfig` mocks before the mechanism is even observable (criterion-8 penalty).
- **C4 rejected** — smallest codebase, but its prize-claim entrypoint is `onlyClaimer` (privileged → the
  selection rules deprioritize privileged-only), and the ERC4626 surface is among the most-audited here
  (high duplicate + intent ambiguity).
- **C1 selected** — uniquely satisfies all ten selection criteria: fresh holdout with an **empty**
  `findings/{raw,validated}` (→ `duplicate_unknown`), deploy-light (no oracle/RPC/bridge), genuinely
  unprivileged value-bearing entrypoints, a crisp one-sentence mechanism, source-answerable reachability,
  and a feasible corrected-reference that uses **only real production code** (prompt
  `processExpiredLocks`).

## Duplicate status
`audits/abracadabra-2024-03-holdout/findings/{raw,validated}` are **empty** and no local answer key mentions
`LockingMultiRewards` → **duplicate_unknown**. Per the project rule, `duplicate_unknown` carries **no**
novelty inference (`novelty_clear=unknown`).
