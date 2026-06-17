# P273 — COVERAGE_ROUTER_SPEC

Deterministic router that classifies advisory candidates into award classes and routes representatives ACROSS classes
before filling slots within a class. Sits between P267 selector and P269 triage. Advisory only.

## Input (per candidate; source-derivable, NOT award labels)
`id` · `locus`/`function`/`contract` · `signals` (free-text/keyword list from the locus + templates) · `templates`
(T1..T9) · `recall_delta` (bool) · `impact_supported` (bool) · `prioritizer_score` · `selector_outcome` (P267) ·
`poc_feasibility` · `feasibility_blockers`.

## Class taxonomy (11) + signal keywords
1. **ACCOUNTING_LIQUIDATION_BAD_DEBT** — collateral, borrow, debt, liquidat, bad_debt, reserve, fee, position/global,
   public/private collateral, solvency, health.
2. **ACCESS_CONTROL_AUTHORIZATION** — onlyOwner, role, ACL, permission, auth, update/admin/config, arbitrary recipient/
   target, bypassable, trusted caller, setter.
3. **ORDER_VALIDATION** — order fill/cancel/update, tokenIn/Out, maker/taker, signature/nonce, amount bounds, slippage/
   deadline, fillable, partial fill, execution recipient, price validation.
4. **FRONT_RUNNING_MEV** — public fill/execution, mutable order state, predictable settlement, missing commitment,
   stale quote, replace/cancel/fill race, callback.
5. **DOS_LIVENESS** — unbounded loop, enumerable user set, revert-blocks-all, gas-dependent progress, stuck queue,
   claim/distribution failure, liquidation/redemption blockage, griefable.
6. **ORACLE_PRICING** — oracle, price feed, TWAP, getReserves, latestRoundData, staleness.
7. **SHARE_ROUNDING_PRECISION** — shares, mint/burn rounding, decimalsOffset, virtual shares, precision, mulDiv.
8. **REWARDS_CLAIMS** — reward, claim, distribute, harvest, accrue, epoch.
9. **STATE_MACHINE_LIFECYCLE** — init, finalize, withdrawal/redeem state, snapshot, lifecycle, status transition.
10. **EXTERNAL_INTEGRATION** — external call, hook, integration, bridge, beacon, masterchef, LP wrap/unwrap.
11. **UNKNOWN_OTHER** — no class signals.
A candidate's class = the class with the most matched signal keywords (deterministic tie-break by class order).

## Scoring + plausibility
`class_signal_strength(candidate)` = matched-keyword count for its class. A candidate is **plausible for routing** iff
`impact_supported != false` AND (`recall_delta` OR `class_signal_strength >= min_signal`) AND
`selector_outcome != REFUTE_*_FIRST`. (Anti-drama: a refuted/unsupported candidate is never a routed representative.)

## Coverage selection (the anti-monoculture core)
1. Group plausible candidates by class; per class keep the best by (class_signal_strength desc, recall_delta,
   prioritizer_score).
2. Rank classes by their best candidate's signal strength (+recall_delta bonus).
3. **Round-robin route ≥1 representative per distinct plausible class** up to `max_classes` (default 5), THEN fill
   remaining `poc_budget` slots with second representatives of the strongest classes (≤ `max_reps_per_class`,
   default 2).
4. **Anti-monoculture hard rule:** ACCOUNTING_LIQUIDATION_BAD_DEBT may not take >1 slot while any of
   {ACCESS_CONTROL_AUTHORIZATION, ORDER_VALIDATION, FRONT_RUNNING_MEV, DOS_LIVENESS} has a plausible unrouted
   representative. (Generalized: no class takes a 2nd slot while a distinct plausible high-signal class has 0.)
5. Heavy candidates (feasibility heavy / harness-weight blocker) → `COVERAGE_SELECT_HEAVY` (still routed).

## Candidate labels
`COVERAGE_SELECT` · `COVERAGE_SELECT_HEAVY` · `COVERAGE_CONTROL` (plausible but a low-priority control kept only if
budget remains) · `COVERAGE_DEFER_LOW_SIGNAL` · `COVERAGE_DEFER_DUPLICATE_CLASS` (class already represented, budget
spent) · `COVERAGE_DEFER_INFEASIBLE` · `COVERAGE_UNKNOWN`.

## Budget
`max_classes` 3–5; `max_reps_per_class` 1–2; `poc_budget` (total SELECT_*) default 5; config caps within hard maxima
(max_classes ≤ 8, poc_budget ≤ 10).

## Advisory contract + guard
Every decision: `severity:null` · `reportable/submission_ready/concluded/emits_finding/production_routing=false` ·
`status:ADVISORY_COVERAGE_DECISION`. Output also: selected_classes, representatives-per-class, class_rationale,
skipped_classes+why, handoff_queue (the SELECT_* ids → P269). Runtime guard fails closed (exit nonzero, no output) on
any leakage / unknown label. Config validation + malformed/missing input fail closed. Bounded output. No answer key.
