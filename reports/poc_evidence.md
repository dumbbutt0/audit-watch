# PoC Evidence Report

Generated: 2026-05-13 15:22

## Summary

| Status | Count |
|--------|-------|
| ✅ proved | 7 |

**7 bugs proved** out of 7 attempted.

## Proved Findings

---

## PoC Evidence: AC-003

**Severity:** MEDIUM
**Status:** ✅ PROVED
**Repair cycles:** 0

### Claim proved

An attacker can call verifyDeposit with a valid proof while snapTimestamp is 0, removing a deposit from the depositList before the next verifyBalances cycle. This causes verifyBalances to undercount totalDepositsWei (the removed deposit is no longer in the list), but the deposit's ETH is now counted in the validator's beacon chain balance which may not yet be verified. This creates a temporary win

### Test

`pocs/k2/AC-003/src/lib.rs`

### Command

```bash
cargo test --manifest-path pocs/k2/AC-003/Cargo.toml -- --nocapture
```

### Output

```
=== AC-003 ACCOUNTING DRIFT IMPACT ===
  BUG CONFIRMED: 32000000000000000000 wei (32 ETH) underreported to vault
=== AC-003 FIX VERIFICATION ===
=== AC-003 PoC: verifyDeposit() missing access control ===
  BUG CONFIRMED: attacker cleared deposit; next verifyBalances will
=== AC-003 PoC: verifyDeposit() missing access control ===
=== AC-003 FIX VERIFICATION ===
  BUG CONFIRMED: attacker cleared deposit; next verifyBalances will
```

### Security impact

All 3 tests pass: (1) attacker calls verifyDeposit while snapTimestamp==0, deposit removed without revert; (2) fixed version blocks attacker; (3) accounting drift: 32 ETH underreported to vault after premature removal.

### Next steps

- Escalate to L3 Foundry fork test
- Verify beacon proof is permissionlessly callable on-chain


---

## PoC Evidence: DS-002

**Severity:** MEDIUM
**Status:** ✅ PROVED
**Repair cycles:** 0

### Claim proved

The test `poc_ds_002_zero_slippage_sandwich_loss` demonstrates that passing `[0, 0]` as minimum withdrawal amounts in `withdrawAll()` provides zero slippage protection against sandwich attacks. Running `cargo test --manifest-path pocs/k2/DS-002/Cargo.toml -- --nocapture` produces: In a balanced pool (WETH=1000, OETH=1000), the strategy holds 200 LP tokens (10%) worth a fair 100 WETH + 100 OETH. Af

### Test

`pocs/k2/DS-002/src/lib.rs`

### Command

```bash
cargo test --manifest-path pocs/k2/DS-002/Cargo.toml -- --nocapture
```

### Output

```
=== DS-002 PoC: Zero-slippage sandwich attack on withdrawAll ===
=== BUG CONFIRMED ===
```

### Security impact

The test `poc_ds_002_zero_slippage_sandwich_loss` demonstrates that passing `[0, 0]` as minimum withdrawal amounts in `withdrawAll()` provides zero slippage protection against sandwich attacks. Running `cargo test --manifest-path pocs/k2/DS-002/Cargo.toml -- --nocapture` produces: In a balanced pool (WETH=1000, OETH=1000), the strategy holds 200 LP tokens (10%) worth a fair 100 WETH + 100 OETH. After an attacker front-runs with a 500 WETH swap (tilting pool to WETH=1500, OETH=666), the strategy's `withdrawAll` with `[0,0]` min amounts accepts only 66 OETH instead of 100 — a 34% OETH shortfall.

### Next steps

- None — ready to submit


---

## PoC Evidence: FL-001

**Severity:** MEDIUM
**Status:** ✅ PROVED
**Repair cycles:** 0

### Claim proved

A privileged attacker (operator or strategist) can flash-loan large amounts into the Curve pool, inflate get_virtual_price(), then trigger rebase() in the same block to artificially increase OETH/OETHb supply beyond real backing. Normal rebasing holders receive inflated yield that is not backed by real assets, diluting the protocol's real backing ratio. Over multiple executions, this erodes the 1:

### Test

`pocs/foundry/test/FL001_VirtualPriceOracle.t.sol`

### Command

```bash
forge test --root pocs/foundry --match-contract FL001_VirtualPriceOracle_PoC -vvv
```

### Output

```
Ran 4 tests for test/FL001_VirtualPriceOracle.t.sol:FL001_VirtualPriceOracle_PoC
[PASS] test_baseline_check_balance_at_fair_price() (gas: 25459)
[PASS] test_poc_fl001_fix_reference_time_averaged_price() (gas: 21376)
[PASS] test_poc_fl001_imbalanced_deposit_inflates_check_balance() (gas: 36948)
[PASS] test_poc_fl001_tvm_overstatement_magnitude() (gas: 53492)
Suite result: ok. 4 passed; 0 failed; 0 skipped
```

### Security impact

The test `test_poc_fl001_imbalanced_deposit_inflates_check_balance` demonstrates that a large one-sided deposit into the Curve OETH/WETH pool inflates `get_virtual_price()`, causing `checkBalance()` to overstate the strategy's TVL. After adding 500 WETH in a single imbalanced deposit, the virtual price rises from 1.000 to ~1.004 (a ~0.4% increase), and checkBalance overstates TVL by the corresponding amount proportional to the strategy's LP holdings. `test_poc_fl001_tvm_overstatement_magnitude` confirms that 10 sequential 100 WETH imbalanced deposits produce >10 BPS TVL overstatement. `test_po

### Next steps

- None — ready to submit


---

## PoC Evidence: FL-002

**Severity:** MEDIUM
**Status:** ✅ PROVED
**Repair cycles:** 0

### Claim proved

An MEV attacker can sandwich the strategy's deposit transactions to steal LP token value. Over time, with sufficient liquidity, this can extract a meaningful fraction of each deposit. Conversely, an attacker can grief withdrawals by temporarily inflating the virtual price to cause revert of remove_liquidity_one_coin operations, blocking the strategist from rebalancing the pool.

### Test

`pocs/foundry/test/FL002_DepositSlippageOracle.t.sol`

### Command

```bash
forge test --root pocs/foundry --match-contract FL002_DepositSlippageOracle_PoC -vvv
```

### Output

```
Ran 5 tests for test/FL002_DepositSlippageOracle.t.sol:FL002_DepositSlippageOracle_PoC
[PASS] test_baseline_fair_vp_deposit_slippage() (gas: 25612)
[PASS] test_poc_fl002_fix_vp_circuit_breaker_detects_inflation() (gas: 32951)
[PASS] test_poc_fl002_inflated_vp_raises_min_withdraw_causes_dos() (gas: 35750)
[PASS] test_poc_fl002_inflated_vp_weakens_deposit_slippage() (gas: 35775)
[PASS] test_poc_fl002_slippage_weakening_proportional_to_inflation() (gas: 985939)
Suite result: ok. 5 passed; 0 failed;
```

### Security impact

test_poc_fl002_inflated_vp_weakens_deposit_slippage proves that a 500 WETH imbalanced deposit inflates get_virtual_price() and reduces the computed minMintAmount for strategy deposits, weakening slippage protection. test_poc_fl002_inflated_vp_raises_min_withdraw_causes_dos proves the same inflation raises minWithdrawAmount for removals, reducing the safety margin before DoS. test_poc_fl002_slippage_weakening_proportional_to_inflation confirms the weakening scales with inflation magnitude (larger attack = more weakening). Circuit-breaker fix test shows actual ~40 BPS VP increase exceeds a 20 BP

### Next steps

- None — ready to submit


---

## PoC Evidence: FL-003

**Severity:** MEDIUM
**Status:** ✅ PROVED
**Repair cycles:** 0

### Claim proved

An attacker can cause the strategy to mint excess OETHb (via mintForStrategy) at a flash-loan-manipulated price. The excess OETHb deposited into the pool at an unfavorable tick ratio is effectively backing a larger OETHb supply than the WETH actually deposited warrants. The _solvencyAssert() at the end of _rebalance() checks vault solvency (99.8% threshold), which provides a backstop, but an attac

### Test

`pocs/foundry/test/FL003_Slot0OracleMint.t.sol`

### Command

```bash
forge test --root pocs/foundry --match-contract FL003_Slot0OracleMint_PoC -vvv
```

### Output

```
Ran 4 tests for test/FL003_Slot0OracleMint.t.sol:FL003_Slot0OracleMint_PoC
[PASS] test_baseline_fair_price_normal_mint() (gas: 471126)
[PASS] test_poc_fl003_slot0_manipulation_causes_excess_oethb_mint() (gas: 20087)
[PASS] test_poc_fl003_twap_would_prevent_manipulation() (gas: 21582)
[PASS] test_poc_fl003_upper_tick_manipulation_over_mints_oethb() (gas: 9883)
Suite result: ok. 4 passed; 0 failed; 0 skipped
```

### Security impact

The test `test_poc_fl003_upper_tick_manipulation_over_mints_oethb` proves that pushing the Aerodrome Slipstream pool's slot0 sqrtPriceX96 toward the upper tick (OETHb-scarce direction) increases the amount returned by `estimateAmount1`, causing `mintForStrategy` to mint more OETHb than fair price warrants. `test_poc_fl003_slot0_manipulation_causes_excess_oethb_mint` confirms any slot0 deviation from fair price (either direction) changes the OETHb amount, proving the protocol uses unprotected slot0. `test_poc_fl003_twap_would_prevent_manipulation` shows a stable TWAP price would mint less OETHb

### Next steps

- None — ready to submit


---

## PoC Evidence: FL-006

**Severity:** MEDIUM
**Status:** ✅ PROVED
**Repair cycles:** 0

### Claim proved

An MEV bot can manipulate the Aerodrome pool spot price before a liquidity removal, causing the strategy to receive predominantly OETHb instead of WETH. Since OETHb must be burned (not sent to the vault as real yield), the effective WETH recovered is less than expected, creating a shortfall in vault withdrawals. The protocol may be unable to fulfill pending withdrawal queue requests.

### Test

`pocs/k2/FL-006/src/lib.rs`

### Command

```bash
cargo test --manifest-path pocs/k2/FL-006/Cargo.toml -- --nocapture
```

### Output

```
=== FL-006 PoC: zero-slippage sandwich attack ===
  BUG CONFIRMED: no slippage protection — sandwich succeeds silently
=== FL-006 Test 1: baseline in-range ===
=== FL-006 Test 4: vault withdrawal shortfall ===
  BUG CONFIRMED: withdrawal queue cannot be fulfilled.
=== FL-006 Test 3: slippage protection ===
======================================================
======================================================
```

### Security impact

The test `poc_fl_006_zero_slippage_sandwich` demonstrates that `_removeLiquidity` in AerodromeAMOStrategy calls `decreaseLiquidity` with `amount0Min=0` and `amount1Min=0`, providing zero slippage protection against sandwich attacks. Running `cargo test --manifest-path pocs/k2/FL-006/Cargo.toml -- --nocapture` produces:

  BUG CONFIRMED: no slippage protection — sandwich succeeds silently
  WETH received: 0 (expected ~500)
  Shortfall: 1000
  AboveRange, min=0 → WETH=0, OETHb=1000 — NO REVERT (BUG)
  AboveRange, min=495 → REVERTED (protected)
  All assertions passed — BUG CONFIRMED

The test ar

### Next steps

- None — ready to submit


---

## PoC Evidence: LG-001

**Severity:** LOW
**Status:** ✅ PROVED
**Repair cycles:** 0

### Claim proved

All liquidity operations (deposit, rebalance, withdrawal) in AerodromeAMOStrategy become permanently reverted when the Sugar helper returns any non-zero WETH rounding dust, effectively bricking the strategy and locking protocol WETH.

### Test

`pocs/foundry/test/LG001_StrictEqualityDoS.t.sol`

### Command

```bash
forge test --root pocs/foundry --match-contract LG001_StrictEqualityDoS_PoC -vvv
```

### Output

```
Ran 4 tests for test/LG001_StrictEqualityDoS.t.sol:LG001_StrictEqualityDoS_PoC
[PASS] test_baseline_large_liquidity_no_weth() (gas: 6895)
[PASS] test_poc_lg001_all_operations_blocked() (gas: 51175810)
[PASS] test_poc_lg001_fixed_allows_1wei_dust() (gas: 51198977)
[PASS] test_poc_lg001_rounding_produces_1wei_weth() (gas: 51966665)
Suite result: ok. 4 passed; 0 failed; 0 skipped
```

### Security impact

The test `test_poc_lg001_rounding_produces_1wei_weth` scans liquidity values 1..1,000,000 and finds multiple values for which the Q64.96 math in `getAmountsForLiquidity` returns exactly 1 wei WETH (instead of 0) when the pool price is at tick 0 (parity). `test_poc_lg001_all_operations_blocked` proves that calling `updateUnderlyingAssetsBuggy()` with any such liquidity value causes a revert with 'Non zero wethAmount', blocking all deposit/withdraw/rebalance operations that call `_updateUnderlyingAssets`. `test_poc_lg001_fixed_allows_1wei_dust` confirms the fix (`require(_wethAmount <= 1)`) reso

### Next steps

- None — ready to submit
