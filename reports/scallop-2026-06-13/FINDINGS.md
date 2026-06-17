# Scallop Protocol (Sui Move lending) — audit findings

Date: 2026-06-13 · Real hunt, local-only, **nothing submitted**, no finding manufactured.
Repo: `scallop-io/sui-lending-protocol` @ `334e93a` (branch `main`). HackenProof program
(hackenproof.com/programs/scallop-protocol-smart-contract): max **$300k**, KYC + PoC. Deployed mainnet packages:
`protocol` published-at `0xefe8b36d…fddf`, `protocol_whitelist` `0x4c262d…acdf`. 4th Sui-Move target validating
Audit-Watch's Move support ([[project_move_support]]) — a **distinct** lending impl from Suilend (own market/reserve/
sCoin model + x-oracle aggregator + APM, not a Solend port). **Rep requirement: user must confirm ≤80 on dashboard.**

## VERDICT: HONEST NEGATIVE — no permissionless High/Critical found.
Twice-audited (MoveBit 2025-03, Asymptotic 2025-09). The **highest-EV surface — the post-audit NEW liquidation
mechanism** — was deep-traced and is sound; oracle freshness/aggregation, sCoin accounting, and the liquidation
flow conserve. Toolchain proven: `sui move build` + repo suite **53/53 pass** (mainnet env).

## Highest-EV: the post-audit delta (unaudited since Asymptotic 2025-09)
`git diff asymptotic-audit-2025 HEAD` shows the major change is a **rewritten liquidation mechanism**
("New liquidation mechanism, 20% liquidate of total debt each time") — `evaluator/liquidation_evaluator.move`
(+266) and `user/liquidate.move` (130 changed). This newly-written, post-audit code was the prime target. Result:
- **`max_repay_amount`**: gates on `weighted_debts_value > collaterals_value_for_liquidation` (returns 0 if healthy
  → `calculate_liquidation_amounts` asserts `actual_repay>0` ⇒ a healthy obligation reverts). Per-call cap = 20% of
  **total** debt value across all types (`LIQUIDATION_CAP_DIVISOR=5`), converted via `u64::mul_div`
  (overflow-safe decomposition); `$10` dust → full repay. Cap-on-total prevents multi-debt-type splitting abuse.
- **`debt_to_collateral_amount`**: `liquidator = repay·rate·(1+liq_discount)`, `protocol = repay·rate·liq_revenue_factor`;
  discount+revenue bounded by `risk_model` (discount ≤15%, penalty ≤20%). Fresh prices.
- **`calculate_liquidation_amounts`**: caps by available collateral, **scaling all three amounts proportionally**
  when `total_needed > collateral` (bad-debt case → liquidator pays pro-rata, no free seizure).
- **`user/liquidate.move`**: accrues market+obligation interest FIRST, computes on fresh state, reduces debt by
  `actual_repay`, pays liquidator `liq_amount` collateral, routes repay+protocol cut via `handle_liquidation_v2`.
  Flow conserves (see below). No stale-value / wrong-repay / missing-recheck bug.

## Other surfaces — SOUND
- **Oracle** (`evaluator/price.move`, `x_oracle`): `get_price` asserts **`now == last_updated`** (strict same-tx/
  same-second freshness) AND `price_value > 0`; `x_oracle` requires a primary feed + a secondary-match quorum
  (`matched >= required_secondary_match_num`). Stale/single-source/zero price can't be used in liquidation/borrow.
- **Liquidation conservation** (`market.move:270` `handle_liquidation_v2`): repay → `reserve::handle_repay`
  (cash↑, debt↓), protocol collateral → `reserve::handle_revenue`, `collateral_stats::decrease`. Balanced against
  the `liq_amount` paid out + `actual_repay` debt reduction. `handle_inflow` updates the rate limiter.
- **sCoin mint/redeem** (`market/reserve.move`): price = `(cash+debt−revenue)/supply`, **monotonic non-decreasing
  assert**; `floor` on both mint and redeem (favors protocol); balance-sheet `cash` is an internal counter (not
  `balanceOf`) ⇒ donation-immune; `supply==0 ⇒ price 1`.
- **Interest/index** (`borrow_dynamics.move`, `interest_model.move`): `index' = index + index·rate·Δt/scale`;
  piecewise-linear kinked curve; revenue factor; accrued before every value-at-risk action.
- **Flash loan** (`user/flash_loan.move`, `reserve.move`): `FlashLoan<T>` receipt has **no copy/drop** (hot potato →
  repay forced); repay asserts `coin ≥ loan+fee`.
- **decimal / math** (`libs/decimal`, `libs/math/u256.move`): u256 WAD mul/div abort on overflow (not silent);
  `u256::mul_div` decomposes to avoid intermediate overflow.
- **Obligation lock** (`lock_obligation.move`): witness-gated (`force_unlock<T:drop>` → `obligation::set_unlock`
  validates the witness) — integration-lock feature; `force_unlock_unhealthy` deprecated (abort).

## Evidence & method
- Pinned deployed version + **diffed `main` vs both audit tags** to isolate the unaudited delta (the new
  liquidation) and deep-traced it manually (the one place a fresh bug would live).
- Runnable conservation evidence = the repo's own suite (`liquidation_test`, `borrow`/`collateral`/`mint`/`redeem`/
  `repay`/`flash_loan`/`obligation` tests): **`sui move test` 53/53 pass** (toolchain via `sui client switch --env
  mainnet`). For a twice-audited protocol whose risk concentrates in the post-audit delta, the deep delta trace +
  the passing suite are the proportionate evidence (no bespoke harness duplicated here).
- Cross-check: MoveBit (2025-03) + Asymptotic (2025-09) audits — negative result, nothing to exclude.

## Out of scope (not reported)
Privileged-address/leaked-key (admin caps, whitelist); self-exploit; DoS-only (e.g. the sCoin price-monotonicity
assert could in principle abort mint/redeem if backing dropped — by-design, Medium at most); incorrect 3rd-party
oracle data (manipulation would be in scope but validation is sound).

## Bottom line
The new (post-audit) liquidation mechanism — the highest-EV surface — plus oracle, sCoin, interest, flash-loan, and
decimal layers are sound; the liquidation flow conserves; the repo suite passes. No permissionless High/Critical →
**honest negative, not submitted.** Reminder: confirm the program's rep requirement is ≤80 before submitting.
