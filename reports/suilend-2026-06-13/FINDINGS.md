# Suilend (Sui Move lending) — audit findings

Date: 2026-06-13 · Real hunt, local-only, **nothing submitted**, no finding manufactured.
Repo: `solendprotocol/suilend` @ `d5ba83a` (branch `devel` = deployed). Sui Move. suilend pkg published-at
`0x3d4353f3…bc10f` (v20), oracles `0xe84b6491…0eb2b`. Bounty: docs.suilend.fi/security/bug-bounty — Critical 10%
of value-at-risk up to **$250k**, High $50k; **PoC required**; **no KYC**; test on devnet/local only.
Third Sui-Move target validating Audit-Watch's Move support ([[project_move_support]]; after turbos CLMM + Ember
vault) — exercises the **lending** primitive.

## VERDICT: HONEST NEGATIVE — no permissionless High/Critical found.
Suilend is a faithful, heavily-audited **Solend** port; the high-value surfaces match the audited Solana design and
the Sui-port-specific surfaces (capability model, donation-immunity) are correct. Toolchain proven (repo suite
**88/88 pass**); reserve-accounting conservation **PoC-proven** (`tests/zzz_reserve_conservation.move`, 3/3 pass).

## Toolchain (resolved)
`sui move build` initially failed: the *testnet* framework pin (`563c1582…`) is a dead git rev. Fix: `sui client
switch --env mainnet` → the mainnet pin (`868c226…`) resolves; all deps (Pyth/Switchboard/Wormhole/liquid_staking)
fetch and the package builds. `sui move test` runs the repo's full suite green (88/88).

## Reviewed surfaces — all SOUND
- **decimal.move** (u256 WAD): `mul`/`div` use u256 intermediates → Move ABORTS on overflow (not silent); realistic
  values safe, extreme values are a safe abort (Medium DoS at most). Standard Solend WAD.
- **Liquidation** (`obligation.move:699-805`, `reserve.move:998-1016`): `is_liquidatable` gate on refreshed values;
  **highest-borrow-weight** seizure rule; **capped bonus** = `min(configured, (collateral−debt)/debt)` (can't worsen
  LTV); 20% close factor (full only when borrow<$100 or bonus capped); pro-rata settle when collateral < repay×(1+
  bonus); `floor` on withdraw favors protocol. Matches audited Solend; no over-withdraw / heal-then-extract path.
- **Obligation health** (`obligation.move:193-312` `refresh`): borrow capacity uses open-LTV × **lower-bound** price;
  liquidation threshold uses close-LTV; health uses borrow-weight × **upper-bound** price — bound directions are
  conservative (can't be flipped to over-borrow). `refresh` + `assert_no_stale_oracles` run before every
  value-at-risk action (borrow/withdraw/liquidate at lending_market.move:622/755/833/1017).
- **Interest & cToken ratio** (`reserve.move`): `ctoken_ratio = total_supply/ctoken_supply` where
  `total_supply = available_amount(internal u64) + borrowed − unclaimed_spread_fees` → uses the **internal counter,
  not balanceOf** ⇒ **donation/inflation attack blocked**; `MIN_AVAILABLE_AMOUNT=100` guard; `floor` on mint AND
  redeem favors protocol; compound `pow` + spread fee correct.
- **Oracle** (`oracles/pyth.move`, `switchboard.move`, `reserve.move:334-362`): price-identity check, confidence-
  interval bound, staleness abort. `PRICE_STALENESS_THRESHOLD_S = 0` is the **strictest** design (price must be
  refreshed in the same tx/second before use) — conservative, not a gap.
- **ObligationOwnerCap** (Sui-port-specific): cap stores `obligation_id` bound at creation; `borrow`/`withdraw`
  resolve the obligation via `cap.obligation_id` ⇒ **no cap-confusion** (a cap for obligation A can't touch B).
  Permissionless actions (`liquidate`/`repay`) correctly take `obligation_id` directly.
- **rate_limiter.move**: audited Solend sliding-window outflow cap; even-distribution approximation acknowledged;
  cap enforced on every outflow (worst case a known DoS-protection approximation → Medium, arguably by-design).

## PoC-proven conservation (`contracts/suilend/tests/zzz_reserve_conservation.move`, `sui move test`, 3/3 PASS)
Reserve-level invariants on the deposit/redeem + interest surface (the highest-value accounting area):
1. **`test_ctoken_roundtrip_no_profit`** — deposit L → mint cTokens → redeem → fulfill → out L′; asserts `L′ ≤ L`
   across {1, 7, 333, 1000, 99_999, 1_234_567} at a non-integer (2.5) cToken ratio → rounding always favors the pool.
2. **`test_interest_only_grows_ctoken_value`** — over 10 compounding steps the `ctoken_ratio` is monotonically
   non-decreasing → depositors never lose value to a rounding bug.
3. **`test_available_amount_matches_held_balance`** — across interleaved deposits/redeems the internal
   `available_amount` counter stays EXACTLY equal to the real held `Balance` → no value created or leaked
   (accounting-level confirmation of donation-immunity).

## Out of scope (not reported)
Privileged-address / leaked-key attacks; **position-limit & borrow-limit bugs** (explicitly OOS); self-exploited;
DoS (only Medium); incorrect 3rd-party oracle data (oracle *manipulation* would be in scope but the validation is
sound). External audits: Suilend/Solend have prior audits (OtterSec/Zellic lineage) — negative result, nothing to
exclude.

## Bottom line
High-value lending surfaces (liquidation, health, interest/cToken, oracle, rate limiter, decimal) + the
Sui-port-specific capability & accounting model are sound; reserve conservation is PoC-proven. No permissionless
High/Critical → **honest negative, not submitted**. Validates Audit-Watch Move support on a lending target.
PoC: `contracts/suilend/tests/zzz_reserve_conservation.move`.
