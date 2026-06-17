# P144 — Problem Statement

P143 RUNTIME_CONFIRMED the B1 mechanism: the real `NoyaValueOracle.getValue` over-values a 2-hop route
(20e18 vs a corrected 6e18) because the multi-hop loop prices `asset→sources[i]` using the static start `asset`
instead of the loop-carried `quotingToken`. Runtime confirmation is **mechanism evidence only**.

**P144 is a human-gated reachability / impact / severity review** — not a detector phase, not a submission phase.

## Primary question
Does the runtime-confirmed `NoyaValueOracle._getValue` mis-valuation create a **production-reachable,
economically meaningful, in-scope** security impact?

## Method
Source-only review (no code change, no submission): map every consumer of `getValue`/`_getValue`; determine who
can configure multi-hop routes and whether an attacker can influence them; classify each consumer's impact;
build the strongest honest attack path; assign a *provisional* severity hypothesis; and run a local
duplicate/scope pre-check. `runtime_status` is kept strictly separate from `submission_status` throughout.

## Bottom line
- **Value path is source-supported:** oracle output → connector/AccountingManager TVL → `totalAssets()` → ERC4626
  share price → `previewDeposit`/`previewRedeem` (real value movement).
- **Reachability is design-supported but not config-demonstrated locally:** multi-hop `priceRoutes` are an
  intended, maintainer-configured feature; no on-disk config/test exhibits a live ≥2-source route. No external
  attacker can set or select routes.
- **Scope/duplicate:** this is the **known, awarded noya H-03** (local answer key) → not novel for this eval.
- **Decision:** ADVANCE_TO_HUMAN_REVIEW_FINDING (technical merit) **gated by DUPLICATE_KNOWN_LOCALLY**; submission
  stays blocked pending human sign-off and an end-to-end value-path PoC (the P143 PoC proves only the oracle delta).
