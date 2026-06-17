# NAVI core lending (`lending_core` + `oracle`) — audit notes (2026-06-15)

**Target:** `github.com/naviprotocol/navi-smart-contracts` → `lending_core` + `oracle` (HackenProof, Critical up to $300k, POC required).
**Repo HEAD:** `473b093` (lending_core version 24, mainnet published-at `0x1e4a13a0…59cb`; oracle `0x203728f4…6242`).
**Local-only. NOTHING submitted.** Baseline: `lending_core` tests 146/146 pass; `oracle` 94/95 (1 env-sensitive fail from the framework-rev repoint, unrelated to logic).

## Verdict so far: HONEST NEGATIVE on the surfaces deep-traced

NAVI is one of the most-audited Sui protocols (11 in-repo reports, Movebit/OtterSec/Salus/Veridise 2023→2026,
incl. 2026 E-Mode by both MoveBit and Veridise). Every highest-EV surface I line-traced is sound. No
High/Critical found. Consistent with prior mature-Sui-lending hunts (Scallop, Suilend = negatives).

### Toolchain note (reusable)
Build hits the recurring dead-testnet-pin: the navi `Move.lock` (both packages) transitively pins sui-framework
`563c1582…` ("not our ref"). Fix: `sed -i 's/563c15820b27…/5445323ef25a…/g'` in both `Move.lock` (the rev
matching the local `sui 1.72.5` binary, already cached) → builds clean.

## Surfaces deep-traced (all sound)

**Oracle (Critical price-manipulation surface):**
- `oracle_pro::update_single_price_v2` is a permissionless keeper that reads **real** Supra/Pyth/Switchboard
  objects; adaptors assert the on-chain `pair_id` matches the configured feed (`oracle_pro.move:189,196`) → no
  fake-price injection. Dual-source **freshness** (`strategy::is_oracle_price_fresh`), **diff-threshold severity**
  (threshold1/threshold2 + timer), and **range/history** validation (`validate_price_range_and_history`) all
  enforced before writing.
- `oracle::get_token_price` (the lending consumer) returns `valid = value>0 && now-ts<=update_interval`;
  `calculator::calculate_value` asserts `is_valid`. Future timestamps can't underflow (clock monotonic).
- Adaptor decimal conversion (`oracle_utils::to_target_decimal_value_safe`) is correct; negative/zero prices
  collapse to 0 → rejected by the min-price range check.
- `OracleFeederCap::update_token_price` bypasses validation but is a **trusted admin role** (centralization,
  acknowledged in audits).

**Lending core (collateral-bypass / liquidation / theft classes):**
- Health factor (`logic::user_health_factor`) = `collateral_USD / weighted_loan_USD × avg_liquidation_threshold`;
  `is_health = HF ≥ 1`. Borrow additionally requires `HF ≥ threshold/ltv` ⇒ `collateral×ltv ≥ loan` (LTV gate).
  Loan side scaled by `borrow_weight` (conservative).
- `execute_withdraw` re-checks `is_health` after decreasing collateral; `execute_borrow` checks HF after
  increasing debt; `execute_liquidate` gates on `!is_health`. Liquidation close-factor = `liquidation_ratio`,
  bonus bounded, seize = repaid+bonus from collateral (conservation holds; underflow-aborts prevent over-seize).
- `validation.move` = pool-level supply/borrow caps + liquidity. `ray_math` = standard Aave half-up; indices use
  internal scaled counters (donation-immune).
- `flash_loan`: `Receipt` has no abilities ⇒ **hot-potato repay enforced**; `repay` asserts
  `repay ≥ amount + fee_to_supplier + fee_to_treasury`.
- `account::AccountCap` = object-capability auth (owner = cap object id); possession-based, no forgery.

**E-Mode (2026 delta — primary hypothesis, ruled out):**
- `EmodeConfig` is an `{assetA, assetB}` pair; `get_emode_asset` **aborts** for any asset outside the pair.
- Hypothesis: an in-e-mode user holding a non-pair collateral/loan would make `dynamic_liquidation_threshold` /
  `is_health` abort → frozen + un-liquidatable → bad debt. **Ruled out:** `enter_emode` requires an empty
  position (`logic.move:743-747`), and every deposit/borrow path funnels through `lending.move` which enforces
  `verify_emode_support` (collateral: `lending.move:188`; debt: `339`,`365`) → only pair assets can be added
  while in e-mode. `execute_deposit`/`execute_borrow` have only those call sites (incentive_v3 routes through
  `lending::*`). No path lets a non-pair asset into an e-mode position.

**incentive_v3 (in-scope, newest, "reward distribution" class):**
- Reward index pattern is standard (`global_index += rate·dt/total_balance`; `user_reward += balance·Δindex`).
- **Ordering correct:** `update_reward_state_by_asset` is called *before* every `lending::deposit/withdraw/borrow`
  balance change → rewards settle at the old balance, then `user_index` resets.
- No double-claim (`claimed` tracked; repeated rule in one claim yields 0). Global index uses gross
  `total_supply` while user accrues on `effective = supply−borrow` ⇒ Σ effective ≤ total ⇒ **under-distributes**
  (no drain). Borrow fee: user owes `amount+fee`, receives `amount`, HF checks full debt — correct.

**Custody — `pool.move` + `pool_manager.move` (coin conservation / vSUI liquid-staking strategy):**
- `Pool{balance, treasury_balance}`. Managed SUI pools run a yield strategy: idle SUI is staked to Volo vSUI
  (`CERT`); `refresh_stake` rebalances to `target_sui_amount`; `prepare_before_withdraw` unstakes on demand
  before a withdrawal that exceeds liquid balance. `withdraw_balance` (v1) **aborts** for managed pools (forces
  the v2 staking-aware path).
- Solvency accounting is consistent: `original_sui_amount` = Σdeposit+Σrepay − Σborrow − Σwithdraw − Σtreasury
  (via `update_deposit`/`update_withdraw` on every coin movement). `treasury = (liquid + vSUI→SUI) − original`
  = pure staking **yield**; `take_vsui_from_treasury` extracts only that excess, leaving full principal backing
  (admin-gated, `PoolAdminCap`). Insolvency only via external vSUI slashing/depeg (out of scope, bounded by
  `target_sui_amount`).
- The `Bag` SUI→`CoinType` cast in `prepare_before_withdraw` only type-resolves for the SUI pool (the only
  managed pool); temp balance nets to zero (asserted in tests). Permissionless `refresh_stake` / `unstake_vsui`
  can't drain: `MIN_OPERATION_AMOUNT` (1 SUI) + target buffers prevent thrash, and `unstake_vsui` only unstakes
  the caller's own supplied `Coin<CERT>` (no pool funds touched).

**`dynamic_calculator.move` — VIEW-ONLY (confirmed):** zero call sites outside itself/tests (`grep`), so it
never gates an on-chain decision; it's the SDK/UI HF+APY estimator (`is_increase`/`estimate_value` what-if
mirror of `logic.move`). Any discrepancy is an off-chain estimate only — not a fund-loss surface. Math mirrors
`logic.move` correctly (minor: it omits logic's `collateral_value>0` guard, so a what-if with zero collateral
aborts the *view* — informational).

## Not yet deep-traced (lowest EV; admin/config/storage-accessor heavy, heavily audited)
`manage.move` + `oracle/oracle_manage.move` + `oracle/config.move` (admin/config setters, cap-gated),
`adaptor_switchboard` (tiny), full `storage.move` body (state accessors), full `lending.move` entry-wiring
bodies (key call sites + emode/execute_* sites already verified). OOS: `incentive.move`, `incentive_v2.move`.

## Conclusion
**Audit-aware honest negative.** Deep-traced every security-relevant surface across both in-scope packages —
oracle price path, HF/borrow/withdraw/liquidation, the 2026 E-Mode delta, in-scope `incentive_v3` rewards +
borrow fee, flash loan, ray math, account-cap auth, coin custody + the vSUI staking strategy, and the (view-only)
dynamic_calculator. All sound; consistent with NAVI's 11-audit depth and prior mature-Sui-lending negatives
(Scallop/Suilend). No submittable High/Critical. Remaining untraced surface is admin/config/storage-accessor
(lowest EV). Nothing submitted.
