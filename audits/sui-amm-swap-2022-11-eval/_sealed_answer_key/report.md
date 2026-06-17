# Sui-AMM-swap (OmniBTC) — MoveBit Audit Report (Answer Key)

- **Project:** Sui-AMM-swap (OmniBTC) — the first open-source AMM swap on Sui (constant-product DEX).
- **Auditor:** MoveBit · **Timeline:** 2022-11-16 to 2022-11-30 · **Language:** Move (Sui)
- **Source:** https://github.com/OmniBTC/Sui-AMM-swap
- **Received (vulnerable) commit reviewed in this eval:** 2d335380e5deb39a76b135aee89437da75f105fb (2022-11-16, pre-fix)
- **Findings:** 7 total — 6 Medium + 1 Major (all fixed). Major mapped to High (H-1) for scoring.

In-scope modules: `sources/implements.move`, `sources/interface.move`, `sources/event.move`,
`sources/controller.move`, `sources/beneficiary.move`, `sources/math.move`, `sources/comparator.move`.

---

# Issue M-1: Missing constant-product K check after swap in implements.swap_out

**Severity:** Medium · **Affected:** `sources/implements.move` → `swap_out<X,Y>()` (~line 302).

After a swap, the code does not verify that the product of the pool reserves
(`coin_x_reserve * coin_y_reserve`, the constant-product K) is preserved/increased. Because a swap charges a
fee, the post-swap reserve product must be **strictly greater** than the pre-swap product. Without this
invariant assertion a mispriced `get_amount_out` (or a future change to it) could let a swapper extract value
or break the constant-product invariant undetected. Fix: assert
`(coin_x_reserve as u128)*(coin_y_reserve as u128) < (new_reserve_x as u128)*(new_reserve_y as u128)` after the
swap (both `is_order` branches). Bug class: missing post-state invariant re-check (K conservation) in a swap path.

# Issue M-2: MINIMAL_LIQUIDITY subtracted from first LP but never minted or locked in implements.add_liquidity

**Severity:** Medium · **Affected:** `sources/implements.move` → `add_liquidity<X,Y>()` (~line 234).

On the first liquidity injection, `MINIMAL_LIQUIDITY` is **subtracted** from the minted LP
(`initial_liq - MINIMAL_LIQUIDITY`) but never actually minted into `lp_supply`. A locked minimum liquidity is
meant to keep `lp_supply` above zero so the LP unit price cannot be cheaply manipulated (first-depositor /
share-inflation attack). Because the amount is only subtracted (not minted+locked), `lp_supply` does not reflect
it and the manipulation cost is lowered. Fix: `balance::increase_supply(&mut pool.lp_supply, MINIMAL_LIQUIDITY)`
and transfer the resulting min-liquidity LP coin to a burn/holding address (`@controller`). Bug class:
first-deposit / LP-share inflation — minimum liquidity not minted+locked.

# Issue M-3: Multi functions pop_back on unchecked empty vector in interface.multi_add/remove/swap

**Severity:** Medium · **Affected:** `sources/interface.move` → `multi_add_liquidity`, `multi_remove_liquidity`,
`multi_swap` (~lines 139, 190, 209).

These functions call `vector::pop_back` on the incoming `coins_in` / `lp_coin` vectors without first checking the
vector is non-empty. A caller passing an empty vector triggers an abort (`pop_back` on empty) — a logic/DoS
oversight; entry points should validate input length. Fix:
`assert!(!vector::is_empty(&coins_x) && !vector::is_empty(&coins_y), ERR_EMPTY_COINS)` before popping. Bug class:
missing input-length / empty-collection validation → abort/DoS.

# Issue M-4: Wrong event access permission — public emit functions allow event spoofing in event.move

**Severity:** Medium · **Affected:** `sources/event.move` → `added_event`, `removed_event`, `swapped_event`,
`withdrew_event` (all `public fun`).

The event-emit helper functions are `public`, so any external party can call them to emit `AddedEvent` /
`RemovedEvent` / `SwappedEvent` etc. directly, forging events that pretend a real `add_liquidity` /
`remove_liquidity` / `swap` occurred. Off-chain consumers that trust these events can be misled, causing
downstream logic errors. Fix: make the emit functions `public(friend)`. Bug class: missing visibility restriction
on event emitters → event spoofing.

# Issue M-5: First-deposit sqrt precision error sqrt(x)*sqrt(y) instead of sqrt(x*y) in implements.add_liquidity

**Severity:** Medium · **Affected:** `sources/implements.move` → `add_liquidity<X,Y>()` (~line 232).

First-deposit LP is computed as `math::sqrt(optimal_coin_x) * math::sqrt(optimal_coin_y)` (square-root each, then
multiply) instead of `sqrt(optimal_coin_x * optimal_coin_y)` (multiply, then one square root). Taking two floor
square roots and multiplying loses precision versus the single combined root. Fix:
`math::sqrt(math::mul_to_u128(optimal_coin_x, optimal_coin_y))`. Bug class: rounding/precision error in liquidity
math (sqrt order of operations).

# Issue M-6: No interface to modify the controller, centralization risk in controller.move

**Severity:** Medium · **Affected:** `sources/controller.move` / `sources/implements.move` — `@controller`
authority.

The `@controller` address has broad authority (pause/resume, fee withdrawal) but there is no interface to change
it, so it cannot be migrated to a multisig and there is no on-chain recovery on key loss/compromise. Fix: add a
permission-checked `modify_controller` (`controller == sender`) that sets `global.controller = new_controller`.
Bug class: centralization / missing admin-rotation (access-control governance).

# Issue H-1: Missing provided_liq>0 zero-check in add_liquidity causes user fund loss

**Severity:** High (report: Major) · **Affected:** `sources/implements.move` → `add_liquidity<X,Y>()` (~line 203).

`add_liquidity` does not assert that the computed `provided_liq > 0`. If a user supplies amounts of
`coin<X>`/`coin<Y>` too small to mint any LP (rounds to zero), the user's deposited coins are consumed by the pool
but they receive **no** `Coin<LP<X,Y>>` in return — a direct loss of user funds. Fix:
`assert!(provided_liq > 0, ERR_INSUFFICIENT_LIQUIDITY_MINTED)` before minting/returning. Bug class: missing
zero/min-output check on a value-bearing deposit → user fund loss.
