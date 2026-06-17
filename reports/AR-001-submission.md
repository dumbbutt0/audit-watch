# Oracle unit mismatch in liquidation-engine close-factor calculation allows liquidators to seize excess collateral beyond protocol limits

## Description

### Brief/Intro

`calculate_liquidation` in the k2 liquidation engine converts the caller-supplied `debt_to_cover`
to its base-currency value using `wad_mul(debt_to_cover, debt_price)` at `calculation.rs:68`.
This omits two normalization factors that the kinetic-router always applies: `oracle_to_wad`
(scales the raw oracle price to WAD precision) and `10^decimals` (converts raw token units to a
standard denomination). For the protocol's default 14-decimal Reflector oracle and any 6-decimal
debt token (including USDC, a first-class reserve), the result is 100× too small. The close-factor
comparison at line 71 is always false, so the cap never fires. Any liquidator calling
`execute_liquidation` against any undercollateralized USDC borrower seizes the full position in a
single transaction, receiving 60% more collateral than the protocol guarantees.

### Vulnerability Details

**Location:** `contracts/2026-04-k2/contracts/liquidation-engine/src/calculation.rs`, line 68

The close-factor enforcement block (lines 62–75):

```rust
let debt_to_cover_base = k2_shared::wad_mul(env, debt_to_cover, debt_price)?;  // line 68

let actual_debt_to_cover = if debt_to_cover_base > remaining_liquidatable {
    remaining_liquidatable
} else {
    debt_to_cover_base   // ← cap never fires; debt_to_cover_base is always tiny
};
```

`wad_mul(a, b)` computes `a × b / 1e18`. Applied to a raw token amount and a raw oracle price,
it is dimensionally incorrect: it divides by WAD but does not multiply by `oracle_to_wad`
(to bring the price to WAD precision) or divide by `10^token_decimals` (to normalize units).

The kinetic-router's `value_in_base` helper and every call-site in the collateral/debt
accumulation loop apply the correct three-factor formula:

```rust
// kinetic-router/src/calculation.rs, lines 354-359
let value_base = balance_u256
    .mul(&price_u256)
    .mul(&oracle_to_wad_u256)
    .div(&decimals_pow_u256)
    ...
```

**Correct formula:**
```
base = amount × price × oracle_to_wad / 10^decimals
```

**Buggy formula (line 68):**
```
base = wad_mul(amount, price) = amount × price / 1e18
```

**Concrete arithmetic (14-decimal oracle, 6-decimal USDC debt, $1 price):**

| Step | Correct | Buggy (line 68) |
|------|---------|-----------------|
| oracle_to_wad | 10^(18−14) = **10,000** | — (omitted) |
| decimals_pow | 10^6 = **1,000,000** | — (omitted) |
| debt_to_cover | 400 USDC = **400 × 10^6 raw** | same |
| debt_price | $1 = **1 × 10^14** | same |
| debt_to_cover_base | 400e6 × 1e14 × 10,000 / 1e6 = **400 WAD** | 400e6 × 1e14 / 1e18 = **40,000** |
| remaining_liquidatable (50% CF on 500 WAD debt) | **250 WAD** | same |
| cap fires? | 400 WAD > 250 WAD → **YES** | 40,000 << 250e18 → **NO** |

The error factor is `oracle_to_wad / 10^decimals = 10,000 / 1,000,000 = 0.01`: the engine
sees a debt value 100× too small, guaranteeing the close-factor comparison is always false.

### Impact Details

The close-factor cap limits how much of a borrower's position a liquidator can seize in one
transaction, preserving the borrower's opportunity to self-rescue. With the bypass:

- **Who:** Every borrower with a USDC-denominated (or any non-18-decimal token) debt position
  against the protocol's default 14-decimal Reflector oracle.
- **What they lose:** A liquidator covering 400 USDC seizes **440 USDC of collateral** instead
  of the guaranteed maximum of **275 USDC** — an excess of **165 USDC (60% over-seizure)** per
  liquidation transaction.
- **Scope:** The 14-decimal Reflector oracle is the protocol default for all trading pairs.
  USDC is a first-class listed reserve. No special permissions, flash loans, or preconditions
  are required: any liquidator calling the normal on-chain entrypoint triggers the bypass
  automatically and unavoidably.
- **Attacker incentive:** Liquidators are paid by the spread — they cover debt and receive
  collateral worth debt plus the 10% bonus. The bug does not increase the bonus rate, but it
  removes the cap on volume. A liquidator can extract the full bonus on the entire position in
  one transaction instead of being limited to 50% per call. There is also a competitive
  first-mover advantage: liquidation bots race each other on insolvent positions. A bot that
  can take the whole position in one transaction beats every bot planning to take the capped
  half and return later. The incentive is both direct profit and structural — any liquidator
  who does not exploit the bypass is outcompeted by one who does.

**Severity: High** — direct collateral loss to borrowers on every qualifying liquidation,
no preconditions, permissionless. The bypassed invariant is a core protocol safety guarantee,
not a peripheral feature.

### References

- **Bug location:** `contracts/2026-04-k2/contracts/liquidation-engine/src/calculation.rs:68`
- **Correct reference implementation:** `contracts/2026-04-k2/contracts/kinetic-router/src/calculation.rs`, `value_in_base()` (lines 13–27) and call-sites at lines 273–278, 354–359
- **Oracle-to-WAD factor:** `contracts/2026-04-k2/contracts/kinetic-router/src/calculation.rs:106`
- **Fix:** Replace `wad_mul(env, debt_to_cover, debt_price)` on line 68 with the three-factor formula: `amount × price × oracle_to_wad / 10^decimals`, matching `value_in_base()` in the kinetic-router.

---

## Proof of Concept

```bash
cargo test --manifest-path pocs/k2/AR-001/Cargo.toml integrated_test 2>&1
```

Expected output:
```
test integrated_test::integrated::ar_001_close_factor_bypass_with_14decimal_oracle_price ... ok
test integrated_test::integrated::ar_001_l3_execute_liquidation_close_factor_bypass ... ok
test result: ok. 2 passed; 0 failed
```

Both tests import and instantiate `k2_liquidation_engine::LiquidationEngineContract` — the
real production crate. Mock contracts supply controlled account data and oracle prices; all
arithmetic is performed by the live `calculate_liquidation` function at line 68.

Key assertions (annotated):

```rust
// Test 1 — Level 2: proves the cap comparison is always false
// buggy_base (40,000) << close_factor_limit (250 WAD) — cap never fires
assert!(buggy_base < close_factor_limit,
    "buggy wad_mul produces a value 100x too small to trigger the cap");

// correct_base (400 WAD) > close_factor_limit (250 WAD) — cap should fire
assert!(correct_base > close_factor_limit,
    "correct value_in_base exceeds the cap, proving the engine should cap here");

// Test 1 — Level 2: end-to-end over-seizure
// collateral_seized > max_correct_collateral_with_bonus (275 USDC raw)
assert!(collateral_seized > max_correct_collateral_with_bonus,
    "liquidation engine returns collateral for the full uncapped amount");

// Test 2 — Level 3: bypass confirmed through the public entrypoint
// execute_liquidation is the entrypoint a real liquidator calls on-chain
assert_eq!(result.debt_to_cover, debt_to_cover_input,
    "debt_to_cover was never capped — close factor did not fire");

assert!(result.collateral_to_liquidate > max_correct_with_bonus,
    "on-chain execution record contains the full uncapped seizure");
```

---

## Mitigation

Replace the `wad_mul` call on line 68 of `contracts/liquidation-engine/src/calculation.rs`
with the same three-factor normalization the kinetic-router already uses in `value_in_base()`:

```rust
// Before (buggy):
let debt_to_cover_base = k2_shared::wad_mul(env, debt_to_cover, debt_price)?;

// After (correct):
let oracle_config = storage::get_oracle_config(env)?;
let oracle_to_wad = k2_shared::calculate_oracle_to_wad_factor(oracle_config.price_precision);
let debt_reserve_data = /* invoke kinetic_router.get_reserve_data(debt_asset) */;
let decimals_pow = debt_reserve_data.configuration.get_decimals_pow()?;

let debt_to_cover_base = U256::from_u128(env, debt_to_cover)
    .mul(&U256::from_u128(env, debt_price))
    .mul(&U256::from_u128(env, oracle_to_wad))
    .div(&U256::from_u128(env, decimals_pow))
    .to_u128()
    .ok_or(KineticRouterError::MathOverflow)?;
```

This mirrors `value_in_base()` in `contracts/kinetic-router/src/calculation.rs` (lines 13–27)
exactly. Ideally the liquidation engine calls the shared helper directly rather than
re-implementing the formula, so that any future oracle precision changes propagate uniformly
to both code paths.
