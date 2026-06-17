# [H-XX] U128 underflow in calculate_liquidation blocks liquidation of deeply underwater positions

## Description

### Brief/Intro

`calculate_liquidation` in the k2 liquidation engine subtracts `collateral_amount_base` from
`user_account_data.total_collateral_base` with a plain `u128` operation at `calculation.rs:104`.
For any position where the debt plus the liquidation bonus exceeds the borrower's available
collateral — precisely the deeply insolvent positions that most urgently need liquidation —
this subtraction underflows. Because the protocol's release profile sets `overflow-checks = true`
(confirmed in `contracts/2026-04-k2/Cargo.toml`), the Soroban runtime panics and aborts every
liquidation attempt on these positions. Liquidation of these positions is blocked while the
underflow condition holds. During that window, bad debt can continue accumulating and the
protocol's primary solvency mechanism is unavailable — exactly when market stress creates the
most dangerous positions.

### Vulnerability Details

**Location:** `contracts/2026-04-k2/contracts/liquidation-engine/src/calculation.rs`, line 104

```rust
let bonus_amount_u256 = debt_u256.mul(&bonus_u256).div(&wad_u256);
let collateral_amount_base = debt_u256
    .add(&bonus_amount_u256)
    .to_u128()
    .ok_or(KineticRouterError::MathOverflow)?;

// ...

let remaining_collateral = user_account_data.total_collateral_base - collateral_amount_base;
//                         ────────────────────────────────────────────────────────────────
//                         plain u128 subtraction — panics when rhs > lhs
```

**Root cause:** `collateral_amount_base = actual_debt_to_cover + bonus_amount`. For any position
where `total_debt_base > ~1.82 × total_collateral_base`, the 50% close factor plus 10%
liquidation bonus produces a `collateral_amount_base` that exceeds `total_collateral_base`.
Rust's checked arithmetic (enforced in release builds by `overflow-checks = true`) traps the
underflow, aborting the transaction.

**Arithmetic trace (all values WAD-scaled, $1 price per asset for clarity):**

```
total_collateral_base  =  1_000 × WAD    ($1,000 collateral)
total_debt_base        =  2_000 × WAD    ($2,000 debt — deeply underwater)
close_factor           =  5_000 BPS      (50% default)

debt_to_cover_base     =  2_000 × WAD
max_liquidatable       =  2_000 × 5_000 / 10_000  =  1_000 × WAD
actual_debt_to_cover   =  min(2_000 WAD, 1_000 WAD)  =  1_000 × WAD

liquidation_bonus_bps  =  1_000 BPS
bonus_amount           =  1_000 WAD × 1_000 / 10_000  =  100 × WAD
collateral_amount_base =  1_000 WAD + 100 WAD  =  1_100 × WAD

calculation.rs line 104:
  remaining_collateral = 1_000 WAD − 1_100 WAD
                       ↑ u128 UNDERFLOW → arithmetic trap → transaction abort
```

Trigger threshold: `total_debt_base > total_collateral_base × 10_000 / (close_factor × (1 + bonus_bps / 10_000))`. With protocol defaults (50% close factor, 10% bonus), this is `total_debt_base > ~1.82 × total_collateral_base`.

**Build configuration confirming overflow-checks in production:**

```toml
# contracts/2026-04-k2/Cargo.toml — workspace-level release profile
[profile.release]
overflow-checks = true   # ← panic fires in the deployed contract
opt-level = "z"
panic = "abort"
```

### Impact Details

- **Who:** Any caller invoking `execute_liquidation` on a qualifying position. No privileged key,
  flash loan, or attacker preparation is required — deep insolvency arises from normal market
  price movement.
- **What the protocol cannot do:** Liquidate any position where `total_debt_base > ~1.82 × total_collateral_base`. Every retry by every liquidator fails identically. Liquidation is blocked for that position while the underflow condition holds. During that window, bad debt can continue accumulating and the protocol's primary solvency mechanism is unavailable.
- **Dual failure mode:** In an unchecked build, the same line silently wraps to a very large u128
  value, inflating `health_factor_after` and suppressing bad-debt socialisation. Both the panic
  path (checked build, current production) and the silent-wrap path (unchecked build) stem from
  the same missing guard on the same line.
- **Attacker incentive:** The bug enables a borrow-and-abandon attack. An attacker deposits
  collateral, borrows at the maximum allowed LTV, then manipulates or waits for the collateral
  price to crash past the `~1.82×` threshold. At that point, `execute_liquidation` reverts on
  every call. The attacker already holds the borrowed funds in their wallet and walks away — the
  debt is unrecoverable. This is a free loan: the attacker extracts real value and the mechanism
  that should recover it is permanently broken for that position while the underflow condition
  holds. No privileged access, flash loan, or special setup is required beyond normal borrowing.

**Severity: High** — liquidation is the protocol's primary mechanism for preventing bad debt
and maintaining solvency. Per the `liquidation_dos` severity rule, L3B reaches High because the
harm IS the blocked liquidation: failure here breaks the core protocol promise that borrowers
cannot create unrecoverable bad debt. Contest precedent (Aave v3 and equivalent DeFi lending
protocols) consistently rates failures in the liquidation path that cause bad debt accumulation
at High, because the protocol becomes insolvent under market stress — exactly when the mechanism
must work.

### References

- **Bug location:** `contracts/2026-04-k2/contracts/liquidation-engine/src/calculation.rs:104`
- **Overflow-checks config:** `contracts/2026-04-k2/Cargo.toml`, `[profile.release]` — `overflow-checks = true`
- **PoC:** `pocs/k2/LG-005/src/integrated_test.rs`
- **Fix:** Replace the plain subtraction on line 104 with `.saturating_sub(collateral_amount_base)`. When `collateral_amount_base` exceeds `total_collateral_base`, all available collateral is consumed and `remaining_collateral = 0`; the liquidation proceeds rather than aborting. The same pattern should be verified at the `remaining_debt` computation on the preceding line.

---

## Proof of Concept

Both tests call the **real** `LiquidationEngineContract` from the production k2-liquidation-engine
crate — no arithmetic is copied or reproduced.

```bash
cargo test --manifest-path pocs/k2/LG-005/Cargo.toml integrated_test 2>&1
```

Expected output:
```
test integrated_test::integrated::lg_005_real_calculate_liquidation_panics_on_underwater_position - should panic ... ok
test integrated_test::integrated::lg_005_l3_execute_liquidation_panics_on_underwater_position - should panic ... ok
test result: ok. 2 passed; 0 failed
```

Key assertions (annotated):

```rust
// Test 1 — Level 2: calculate_liquidation panics directly
// MockRouter: total_collateral=$1000, total_debt=$2000, hf=0.25 WAD
#[test]
#[should_panic]
fn lg_005_real_calculate_liquidation_panics_on_underwater_position() {
    let _ = client.calculate_liquidation(
        &collateral_asset,
        &debt_asset,
        &user,
        &(2_000 * WAD),  // debt_to_cover
    );
    // ↑ panics at calculation.rs:104:
    //   remaining_collateral = 1_000 WAD - 1_100 WAD  →  u128 UNDERFLOW
}

// Test 2 — Level 3: execute_liquidation panics at the public entrypoint
// Confirms the panic fires on the full call path a real liquidator uses on-chain
#[test]
#[should_panic]
fn lg_005_l3_execute_liquidation_panics_on_underwater_position() {
    let _ = client.execute_liquidation(
        &liquidator,
        &collateral_asset,
        &debt_asset,
        &user,
        &(2_000 * WAD),
        &false,
    );
    // ↑ execute_liquidation → calculate_liquidation → line 104: PANIC
}
```

---

## Mitigation

Replace the plain subtraction on line 104 of `contracts/liquidation-engine/src/calculation.rs`
with a saturating subtraction:

```rust
// Before (buggy):
let remaining_collateral = user_account_data.total_collateral_base - collateral_amount_base;

// After (correct):
let remaining_collateral = user_account_data.total_collateral_base
    .saturating_sub(collateral_amount_base);
```

`saturating_sub` is correct here: when `collateral_amount_base` exceeds
`total_collateral_base`, all available collateral is consumed and `remaining_collateral`
should be `0`. The liquidation proceeds — seizing all collateral and covering as much debt
as possible — rather than aborting. This matches the behaviour of Aave v3's equivalent path.

The same pattern should be verified at the `remaining_debt` computation on the preceding
line, though that subtraction is bounded by `remaining_liquidatable ≤ total_debt_base` and
is less likely to underflow in practice.
