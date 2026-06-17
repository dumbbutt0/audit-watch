# Momentum mmt-v3-core (Sui Move CLMM) — audit findings

Date: 2026-06-13 · Real hunt, local-only, **nothing submitted**, no finding manufactured.
Source: user-provided private repo zip (`mmt-v3-core-main.zip`) extracted to `/tmp/momentum-hunt/mmt-v3-core-main/clmm/`.
Package `mmt_v3` v1.0.0, published-at `0xcf60a40f…c3c1d1` (Sui mainnet). HackenProof (Critical, PoC required, KYC,
invite-only). **This was the original motivating target** for the whole Move build; the turbos hunt was its dry run.

## VERDICT: HONEST NEGATIVE — no permissionless High/Critical found in the CLMM core.
Momentum mmt-v3 is a professionally-built, **post-Cetus** `integer-mate` CLMM (same quality class as turbos). I
re-derived every value-critical surface from source (No-Trust). Toolchain confirmed: `sui move test` → **364/364
repo tests pass** (lowercase `move.toml` symlinked to `Move.toml`; `sui client switch --env mainnet`).

## The Cetus-class lead — re-confirmed CLEAN (the whole reason for this hunt)
`mmt_v3::math_u256::checked_shlw` (math_u256.move:21-28) uses `mask = 1 << 192` → overflow iff `n ≥ 2^192`, so
`n<<64` always fits u256. This is the **correct** post-Cetus form; the $220M Cetus hack was a *wrong* mask here.
All call sites `assert!(!overflow)`: `liquidity_math.move:35`, `sqrt_price_math.move:22/68/122`. The y-side
(`get_amount_y_*`) uses `full_mul(u128,u128)→u256 / Q64` which **cannot** overflow u256, then a **checked** `as u64`
downcast. The Cetus-class vulnerability is **not present**.

## Reviewed and SOUND (re-derived from source)
- **Integer/liquidity/sqrt math** (`integer-mate/`, `utils/liquidity_math.move`, `utils/sqrt_price_math.move`,
  `full_math_u128`): `checked_shlw` correct; `div_round` rounding direction correct (amounts via the `round_up`
  arg, used pool-favoring by callers); `get_next_sqrt_price_*` clamp to `[min,max]_sqrt_price` and assert; every
  `as u64`/`as u128` is a checked (abort-on-overflow) downcast. `add_delta` (liquidity_math.move:7) guards
  underflow/overflow.
- **Swap step** (`utils/swap_math.move::compute_swap_step`): faithful UniV3 — `amount_in` rounds **up** (`true`),
  `amount_out` rounds **down** (`false`) ⇒ pool-favoring; fee handling standard.
- **Swap loop + tick crossing** (`actions/trade.move`): next-initialized-tick within one word, clamped to
  MIN/MAX tick; `compute_swap_step`; protocol-fee split (`mul_div_floor`); `fee_growth_global += fee·Q64/liquidity`
  (`wrapping_add`); on crossing, `liquidity_delta = tick::cross(...)` and **`liquidity_change = neg(delta)` when
  `is_x_to_y`** with new active tick `tick_next − 1` — the correct UniV3 sign. Output taken from reserves; input
  owed via `FlashSwapReceipt`.
- **Flash swap / flash loan** (`trade.move`): `FlashSwapReceipt`/`FlashLoanReceipt` have **no abilities** (hot
  potato → forced consume). `repay_flash_swap` asserts `initial_reserve + debt ≤ final_reserve`; `repay_flash_loan`
  asserts `before + amount + fee ≤ after`, splits protocol fee, credits remaining fee to `fee_growth_global` (LPs).
  Pool-bound (`verify_pool`). No borrow-without-repay; flash loan requires `amount < reserve` (can't drain 100%).
- **Position fee/reward accrual** (`storage/position.move::update`): `fee_growth_delta` computed on the **old**
  `position.liquidity` (correct ordering, before the liquidity update), `mul_div_floor` (pool-favoring),
  `wrapping_sub` for fee/reward growth; `owed_coin`/`coins_owed_reward` bounded by `add_check`; claims subtract from
  owed (u64 underflow-aborts) ⇒ **no over-claim**. Reward uses old liquidity too.
- **Liquidity add/remove** (`actions/liquidity.move`): thin orchestration over `pool::add/remove_liquidity` with
  slippage checks (`delta ≥ min` / `balance ≥ min`); position ownership enforced by Sui object possession;
  `close_position` requires `is_empty`. Heavy math delegates to the verified `liquidity_math`/`position`/tick layer.
- **Signed-int tick math** (`i32`/`i64`/`i128`, `storage/tick.move`): two's-complement with explicit
  overflow-detection in `add`/`sub`; `tick.liquidity_net` sign (lower add / upper sub); fee-growth-outside
  `wrapping_sub` (intended UniV3 wrap). (Verified via direct read of the math + tick crossing.)

## Reviewed in depth (second pass — oracle + pool add/remove + reward machinery)
- **`utils/oracle.move`** — faithful UniV3 oracle. `binary_search` cannot underflow `high = mid_index - 1`:
  `get_surrounding_observations` asserts the oldest obs `ts ≤ target` before calling, so the oldest slot always
  takes the `low = mid+1` branch; for any other slot `mid_index ≥ next_index ≥ 1`. `transform` time-weighted
  interpolation guards div-by-zero (the `time_diff==0` branch is unreachable — it implies `target==earlier==later`).
  `grow` caps cardinality `< 1000`; `write` is idempotent within the same second (≤1 observation/sec/pool, so fee
  collection cannot spam the ring). `seconds_per_liquidity` uses `overflow_add` (intended wrap).
- **`storage/pool.move` add/remove (`update_data_for_delta_l`)** — correct UniV3 ordering: reward/fee growth settled
  on the **old** liquidity (step [1]/[4] before the step [6] global-liquidity update); global `pool.liquidity`
  changed only when current tick ∈ `[lower,upper)`; `delta_x/y` via `get_amounts_for_liquidity` rounds **up on add,
  down on remove** (pool-favoring); deposit two-step (`get_liquidity_for_amounts` floors liquidity, then re-derives
  amounts rounded up, `assert balance ≥ delta`) — any off-by-one only reverts the deposit (no value creation).
- **Reward accounting (`update_reward_infos` + `position::update_reward_infos` + `tick::compute_reward_growths`)** —
  conservation holds and is protocol-favoring. `total_reward_allocated ≤ total_reward` (rate =
  `remaining_reward·Q64/remaining_duration`, floored; allocation = `time·rate/Q64`, floored). Per-LP owed (growth
  floored) ≤ allocated ≤ funded custodian. Late-added rewards attribute correctly: a reward starts at `global=0`, so
  treating a pre-existing tick's missing `reward_growths_outside[i]` as `0` (the `compute_reward_growths` default) is
  equivalent to initializing every tick's outside at `global=0` — the standard UniV3 convention. `cross()`'s checked
  subtractions stay non-negative by cumulative-monotonicity (proved for `seconds_per_liquidity`/`seconds_out_side`).
  Admin rate changes (`update_pool_reward_emission`) settle via `update_reward_infos` first (admin.move:117,143).
- **Full swap loop (`actions/trade.move`)** — `flash_swap`/`compute_swap_result` are the canonical UniV3 machine;
  `compute_swap_step` caps exact-output at `amount_remaining` (swap_math:131, no underflow); protocol-fee split +
  `fee_growth_global` (Q64, `wrapping_add`) committed at swap time, input arrives at repay (hot-potato enforced —
  `FlashSwapReceipt`/`FlashLoanReceipt` are abilityless). `repay_flash_swap` asserts `init+debt ≤ final`;
  `repay_flash_loan` asserts `before+amt+fee ≤ after`, splits protocol/LP fee. Reserve conservation holds across the
  flash window (fee tokens stay in reserve, backing both `protocol_fee` and `fee_growth`).
- **`actions/liquidity.move`** — `open_position`/`add_liquidity` both enforce `verify_tick` + the Momentum-specific
  `check_tick_range` (min range width); slippage via `min_amount_x/y`; excess refunded.
- **`actions/create_pool.move` + `global_config`** — pool creation requires an admin-registered fee tier
  (`get_tick_spacing` aborts otherwise); `enable_fee_rate` asserts `fee_rate < 1_000_000` and `0 < spacing < 10_000`,
  so swap_math's `denom − fee_rate` can never underflow. Coin order canonicalized (`check_coin_order`).
- **`app.move` (ACL)** — `AdminCap`-gated admin-address assignment; privileged ops assert `sender == configured
  admin`. No permissionless privileged path.
- **`slippage_check` package** — single thin post-swap `assert_slippage` helper (price floor/ceiling vs final
  `sqrt_price`); correct. (Nit: magic abort code `111`.)
- `storage/tick_bitmap.move` — flip + next-initialized share one `position()` mapping (internally consistent;
  exercised by the trade tests). `version/version.move` — version gate (privileged, OOS for permissionless).

**Coverage: every production `.move` in both packages (`clmm` + `slippage_check`) has been line-read.**

## Info / defensive notes (no impact — not submittable)
- **`pool::safe_withdraw` (line 888)** clears the position's owed (fee/reward) debt *then* pays `min(amount, balance)`.
  If reserves/custodian were ever short, the user's debt is zeroed but they receive less (silent dust loss). **Proven
  unreachable** in practice: conservation guarantees `reserve ≥ Σ obligations` and `custodian = total_reward ≥
  allocated ≥ owed`, so the cap never binds. Defensive-only; worth a one-line audit note.
- **`pool::get_friendly_ticks`** uses `i32::mod` (truncates toward zero), so negative ticks round toward zero, not
  floor-aligned. It is an **unused periphery helper** (no core call site); `verify_tick` enforces exact
  `abs(tick) % spacing == 0` on real position creation, so core alignment is unaffected. Info-only.
- **Oracle write on zero-delta fee collection** (`collect::fee` → `update_data_for_delta_l(0)`): records an accurate
  observation when in-range; bounded to ≤1/sec by `oracle::write` idempotency. Benign (minor gas / extra obs).

## Bottom line
Momentum mmt-v3's CLMM core — integer/sqrt/liquidity math (Cetus-class **clean**), swap loop + tick crossing,
flash swap/loan conservation, position fee/reward accrual, and liquidity add/remove — is the canonical, correct,
post-Cetus construction with pool-favoring rounding, hot-potato flash receipts, and checked downcasts; 364 repo
tests pass. No permissionless High/Critical found → **honest negative, not submitted.** The Cetus-class lead that
motivated the entire Move build is re-confirmed clean (mask `1<<192`). Evidence: the repo's own `sui move test`
suite (364 passing, incl. swap/trade conservation tests) + the per-surface source re-derivation above.
