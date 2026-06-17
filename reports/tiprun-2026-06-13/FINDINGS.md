# TipRun Contracts — audit findings

Date: 2026-06-13 · Real hunt, local-only, **nothing submitted**, no finding manufactured.
Source: user-provided `tiprun-contracts-main.zip` → `/tmp/tiprun-hunt/tiprun-contracts-main/` (commit `d5d4d2a…`).
Target: TipRun, a trustless off-chain-matching / on-chain-settlement exchange (perp/spot/predict profiles),
Foundry, `solc ^0.8.13`, OZ-upgradeable. Active contest.

Toolchain: repo ships empty `lib/`; populated forge-std + OZ 5.4 + solidity-bytes-utils from cache. `src/` builds.
Baseline repo suite: **387 passed / 5 failed**; the 5 failures are `vm.expectRevert` *string* mismatches caused by
the OZ 4.x→5.4 substitution (tests assert legacy OZ revert strings; OZ 5.4 emits custom errors) — test-only
artifacts, not contract bugs. `script/` + 2 e2e + 2 unit tests that use the removed OZ 4.x `ProxyAdmin` API were
moved aside / had their `new ProxyAdmin()` patched to `new ProxyAdmin(msg.sender)` (scaffolding, not audited `src/`).

---

## F-1 (HIGH / CRITICAL) — Maintenance-margin check lets a user withdraw 100% of collateral while holding an open position (margin bypass → bad debt)

**Contract:** `src/core/risk/Risk.sol :: checkValidTransition` (the `CAP_MARGIN_CHECK` provider, wired by `RiskPlugin`
in the `perp` profile and invoked by `PositionManager.updatePosition` on **every** position/collateral change).

**Status:** CONFIRMED with a passing Foundry PoC (`test/PoC_MarginBypassWithdraw.t.sol`), corroborated by the
project's own test `test/PositionManager.Risk.t.sol::test_ArithmeticEdgeCase_NegativeCollateral`.

### Root cause
`checkValidTransition` is meant to enforce maintenance margin: a transition is allowed only if the **updated**
position is healthy, or (if already unhealthy) it strictly improves. The "you may not reduce value" protection,
however, is gated on `initTotalRisk == 0`:

```solidity
// Risk.sol
if (updatedTotalRisk <= updatedTotalValue * FXP_32_ONE) { return; }      // (A) healthy → allow
...
checkSmallerInSyntheticHoldings(fullInit, fullUpdated);                   // (B) positions may only shrink
if (initTotalValue * updatedTotalRisk < updatedTotalValue * initTotalRisk) { revert("PM: val/risk dec"); } // (C)
if (initTotalRisk == 0) {                                                 // (D) value-decrease guard…
    if (updatedTotalValue < initTotalValue) { revert("PM: val dec"); }    //     …ONLY when risk == 0
}
```

For a **pure collateral withdrawal**, the synthetic holdings are unchanged, so `updatedRisk == initRisk == R`.
Substituting into guard (C): `initValue·R < updatedValue·R` ⟺ `initValue < updatedValue`. Removing collateral makes
`updatedValue < initValue`, so the condition is **false → no revert**. Guard (D) is then skipped because `R > 0`.
Net result: **any account holding a position (R > 0) can decrease its collateral arbitrarily without the margin
check ever reverting** — including straight into a liquidatable / negative-equity state.

Guard (C) is moreover **inverted**: it reverts exactly when the value/risk ratio *increases* (the account gets
healthier) and permits ratio *decreases* (worse). The project's own `test_RiskRatioComparisonLogic` computes
`ratioImproved = initRisk·updatedValue > updatedRisk·initValue`, which is algebraically identical to the contract's
revert condition (C) — i.e. the contract reverts on "ratio improved". (C) only escapes notice because the happy-path
tests all hit the early healthy-return (A).

The project even documents the bypass: `test_ArithmeticEdgeCase_NegativeCollateral` comments *"First create a
synthetic position **to avoid the totalValue decrease restriction**"* and then withdraws 15 000 against 10 000
collateral into **negative** equity — asserting success.

### Impact
On a `perp` deployment, `checkValidTransition` is the *only* maintenance-margin enforcement (the withdrawal
balance-check `Risk.validateWithdrawal` merely requires `bucket-0 collateral ≥ amount`). A user can therefore:
1. deposit collateral, 2. open a leveraged position, 3. **withdraw their entire collateral out of custody** while
the position stays open and unbacked. The user keeps directional exposure financed entirely by the protocol (a free
option): if the position wins they collect; if it loses they have already removed all margin, leaving **bad debt**
borne by the protocol / counterparties / insurance. This breaks the core solvency invariant of the exchange.

Severity: **High–Critical** (depending on the contest's treatment of margin-bypass / protocol-bad-debt). It is a
direct break of the maintenance-margin guarantee with attacker-controlled, permissionless (user-signed) entry.

### PoC (`test/PoC_MarginBypassWithdraw.t.sol`, passes against the perp harness)
- deposit 10 000 collateral; risk factor 2× (`risk = 2 × markValue`); oracle price 1.
- open long 5 000 → value `15 000·FXP`, risk `10 000·FXP²` → **healthy** (`assertLe(r0, v0·FXP)`).
- submit a signed `Withdrawal` for the **full 10 000** through `MultiTransactionProcessor` → **succeeds**.
- after: collateral `0`, position still long 5 000, value `5 000·FXP`, risk `10 000·FXP²` →
  `assertGt(r1, v1·FXP)` holds = **account is now under maintenance margin** yet the withdrawal was allowed;
  `10 000` tokens were transferred out of `LoadingZone` to the attacker (`tokens extracted: 10000`).

Run: `forge test --match-contract PoC_MarginBypassWithdraw -vv`.

### Suggested fix
In `checkValidTransition`, apply the value-decrease / health-non-worsening guard **regardless of `initRisk`**, and
correct the ratio comparison direction so it reverts when the updated value/risk ratio *decreases* (account gets
less healthy), e.g. revert when `updatedValue·initRisk < initValue·updatedRisk` (with explicit handling of negative
`totalValue`). Equivalently: forbid any transition whose result is unhealthy unless it strictly raises the
value/risk ratio. Also have `validateWithdrawal` account for open-position risk, not just raw bucket-0 collateral.

---

## F-2 (HIGH / CRITICAL) — Account freeze / liquidation lock when notional exceeds the top risk segment (attacker can deliberately dodge liquidation)

**Contracts:** `src/core/config/GeneralConfig.sol :: getRiskFactor` + `src/core/risk/Risk.sol :: getAssetValueAndRisk`.
**Status:** CONFIRMED with a passing PoC (`test/PoC_RiskSegmentFreeze.t.sol`).

`getRiskFactor` walks the asset's risk-factor segments and returns `(segment.risk, true)` for the first segment whose
`upperBound` covers the position's notional; if the notional exceeds **every** segment it returns `(0, false)`.
`Risk.getAssetValueAndRisk` then executes `require(riskOk, "Risk: no risk")` and **reverts** (it does not clamp to the
top tier). Because **every** position-touching operation — withdraw, trade, liquidate, deleverage, settlement —
routes through `checkValidTransition → getAccountPositionStatus → getAssetValueAndRisk`, a single asset whose notional
crosses the cap **freezes the entire account**.

Critically, the trigger is a plain **oracle price increase** (`price × balance` is the notional), not any action on the
account. So when an asset pumps — exactly when accounts go underwater and most need liquidating — affected accounts
become **un-liquidatable** (the protocol cannot recover the bad debt) and their owners cannot withdraw or de-risk.
The freeze persists until the price falls back under the cap or an admin reconfigures the asset.

**Attacker-controlled exploitation (short side).** For a short, notional = `price × |amount|` *rises* as the price
rises — i.e. precisely as the short goes **underwater**. An attacker can size a short so that its maintenance-margin
breach occurs at a price above the segment cap; the account then reaches a state that is simultaneously **insolvent
and frozen**, so it can **never be liquidated** and the attacker walks away from the loss → direct protocol bad debt.
This makes F-2 a deliberate exploit, not just an unlucky-price liveness bug.

PoC (`test/PoC_RiskSegmentFreeze.t.sol`, both tests pass):
- `test_PoC_priceRiseFreezesAccountAndBlocksLiquidation`: long 5 000 @ price 1 (notional 5 000 ≤ cap 10 000) healthy;
  raise price to 3 (notional 15 000) ⇒ `getAccountPositionStatus`, any resize/liquidation, and a withdrawal batch
  all revert `Risk: no risk` (account frozen, funds locked).
- `test_PoC_shortDodgesLiquidationByFreezing`: short 3 000 @ price 1 (healthy); raise price to 4 ⇒ equity is
  `10 000 − 4×3 000 = −2 000` (insolvent) yet every liquidation/resize reverts `Risk: no risk` — the insolvent short
  is un-liquidatable. Run: `forge test --match-contract PoC_RiskSegmentFreeze -vv`.

Severity High→Critical (the short variant is attacker-initiated and yields unrecoverable bad debt; config-dependent
only in that it requires a finite top segment — the normal tiered-margin setup). Fix: in `getRiskFactor`, **clamp**
to the last segment's risk when notional exceeds all segments (never return `false`), or handle `riskOk == false &&
priceOk == true` in `Risk` without reverting.

## M-1 (MEDIUM) — `Risk.checkValidTransition` ratio guard is inverted: it blocks legitimate de-risking of an unhealthy account (liveness/DoS)

> **For submission, M-1 is merged into F-1** — same root cause (the inverted comparison at `Risk.sol:133`), one fix.
> See the combined package `submissions/F-1/report.md` (M-1 = "Manifestation B"). The standalone `submissions/M-1/`
> folder now redirects there and is kept only for reproduction.

Same function as F-1, second symptom. In the unhealthy branch, guard (C) `initValue·updatedRisk < updatedValue·initRisk`
reverts exactly when the value/risk ratio **increases** (account gets healthier). So an account that is below
maintenance margin and tries to **reduce** its position (a risk-decreasing trade/deleverage — the legitimate way to
recover) hits `checkSmallerInSyntheticHoldings` (passes, position shrank) then reverts at (C) ("PM: val/risk dec").
Effect: an underwater account cannot self-heal by closing exposure; combined with F-1 (which lets accounts reach the
unhealthy state) this can strand positions. Fix: invert the comparison (revert when the ratio *decreases*) and apply
the health-non-worsening guard unconditionally.

**Status:** CONFIRMED with a passing PoC (`test/PoC_DeriskDoS.t.sol`). From an under-margin state (collateral 2 000 /
long 5 000 ⇒ value 7 000·FXP, risk 10 000·FXP²), a **fair partial de-risk** — sell 500 synthetic for 500 collateral
(value-neutral, risk ↓ to 9 000·FXP², strictly healthier but still under margin) — **reverts with `PM: val/risk
dec`**; the position is left untouched. Only a de-risk large enough to reach *full* health in one step (sell 4 000)
is allowed. With partial orderbook fills, incremental recovery is therefore blocked. All de-risk paths (trade,
deleverage) hit this same gate via `FundingApplyLib.applyAndUpdate → PositionManager.updatePosition`.

## M-2 (MEDIUM / LOW) — Oracle prices have no read-side staleness check and the monotonic-update guard is commented out

`Oracle.getPrice` returns `exist = (timestamp > 0)` with **no freshness check**, and `Oracle.updatePrice` has its
`timestamp > current` monotonic guard **commented out** (TODO). `Risk.getAssetValueAndRisk` treats any stored price
as valid forever. Ingestion (`OraclePriceTickTransLib`) enforces signer-quorum + median + a ≤1-day bound, but once
stored a price is used in all margin/liquidation math indefinitely, and a (recently-signed, ≤1-day-old) price can be
re-applied out of order because the monotonic guard is gone. Under operator delay/failure or reorg, margin decisions
use stale prices. Fix: enforce a max-age on read and restore the monotonic timestamp guard.

## M-3 (MEDIUM, trust-dependent) — Liquidate/Deleverage have no on-chain maintenance-margin precondition

`LiquidateTransLib.process` / `DeleverageTransLib.process` never check that the targeted account is actually below
maintenance margin before force-resizing its position (and `Deleverage` only checks `checkSigner` = "is a registered
signer", with no signature/nonce from the deleveraged user). Both are `onlyTxBatcher`-gated, so exploitation requires
a malicious/buggy operator — but the on-chain safety that "only unhealthy accounts can be liquidated/deleveraged" is
absent. Severity depends on the contest's operator-trust model (Low if the sequencer is fully trusted; Medium/High
if users are protected on-chain from having healthy positions seized). Fix: require the target to be below
maintenance margin (and bound the liquidation price to oracle ± penalty).

## M-4 (MEDIUM / LOW) — `setSyntheticAssetsInfo` does not bump `configVersion`, defeating the stale-config batch guard

`GeneralConfig.setSyntheticAssetsInfo` (which sets risk-factor segments, oracle signers, oracle quorum, max funding
rate, resolution) has its `incrConfigVersionInternal()` **commented out** (lines ~179-182), whereas every other
mutator (`setCollateralAssetInfo`, `setFeeAccountId`, `setMaxFundingRate`, `removeSyntheticAssetInfo`,
`setIsRiskByBalanceOnly`) bumps it. `MultiTransactionProcessor.processMultiTransactions` reverts a batch only when
`configVersion < currentVersion`; since the most security-relevant config (risk params, oracle signer set/quorum) can
change **without** bumping the version, in-flight user transactions execute under the new parameters and the
stale-config guard they rely on never triggers. Fix: bump `configVersion` in `setSyntheticAssetsInfo` for parity.

## L-1 (LOW, trust-dependent) — Settlement uses an unconstrained, unsigned operator price

`SettlementTransLib.process` force-settles a position at `settlementPrice ∈ [0, int128.max]` chosen by the operator,
with no oracle/signature binding. Resolution correctness rests entirely on the trusted operator. Fix: bind the
settlement price to a signed oracle/resolution value.

## L-2 (LOW) — `LoadingZone` uses raw ERC20 calls (no SafeERC20)

`deposit`/`processWithdraw` use `require(token.transfer*(...))` and assume a standard bool-returning, non-fee-on-
transfer token. Non-standard tokens (USDT-style no-return, fee-on-transfer, rebasing) would break deposits or the
`balances`/`systemBalance` accounting. The deposit token is owner-configured (single asset), so impact is limited to
deployment choice. Fix: use `SafeERC20` and measure received amounts.

## L-3 (LOW) — `RegisterAccount` signature does not bind `accountId` (and has no nonce)

`RegisterAccountTransLib.getRegisterAccountHash` hashes `(owner, signers)` only — **not** `accountId` — and the struct
has no nonce. The owner's registration signature is therefore valid for any `accountId`. Mitigated by
`AccountManager.registerAccount` (reverts on an already-registered `accountId` *or* owner address — one-address-one-
account) and the trusted batcher, so it is not a takeover, but the signed intent doesn't bind the ID it authorizes.
Fix: include `accountId` (and a nonce) in the signed struct.

## L-4 (LOW) — Settlement price scale is inconsistent with oracle price scale

Oracle prices are FXP_32-scaled (`1.0 == FXP_32_ONE`) and used as such in `Risk` (`value = amount × oraclePrice`).
`SettlementTransLib` credits `collateralDelta = syntheticBalance × settlementPrice` directly to **raw** collateral
(the doc says "e.g. 1 for YES"), so `settlementPrice` must be raw. Passing an FXP-scaled price by mistake (matching
the oracle convention) over-credits by 2³² and is only bounded by `[0, int128.max]`. Document/validate the scale.

## Info — minor / disproven
- `SignaturesLib.recoverSigner` is raw `ecrecover` with no low-`s` malleability or zero-address guard. Benign here:
  replay is nonce-based and the recovered address is compared against stored permissions (address(0) has none).
- **Disproven lead (negative-amount Transfer theft):** `TransferTransLib` itself lacks an `amount > 0` check (the
  sign would flip both legs, debiting the counterparty), BUT `BalancePlugin.processTransaction` enforces
  `require(transfer.amount > 0, "Invalid amount")` (and the same for deposit/withdraw) before dispatch — so the
  sign-flip is not reachable. PoC reverted with "Invalid amount". Not a finding (recommend adding the check to the
  lib too as defense-in-depth).
- No permissionless escape hatch: `TYPE_FORCED_WITHDRAWAL` (type 3) is deprecated (reverts); all exits route through
  `onlyTxBatcher`. Censorship/liveness is a documented trust assumption.
- Admin (`ALLOW_ADMIN` holder, via `processAdminSetSignerPermissions`) can set arbitrary permissions on any account,
  including granting itself `ALLOW_WITHDRAW` on a victim — documented operator/centralization trust ("be selective").
  Delegation for non-admins is correctly gated (can only grant bits you hold), so no non-admin → admin escalation.

## Surfaces reviewed & sound
- Trade (`LimitOrderLib`/`TradeTransLib`): synthetic + collateral conservation (zero-sum incl. fees), per-order
  price/fee fairness bounds, orderHash re-check on every fill, nonce-on-first-fill. Sound.
- Funding (`Funding`/`FundingApplyLib`/`FundingLib`): cached-index stamping prevents double-apply, sign correct
  (longs pay positive funding), rate bounded by `maxFundingRate`, applied on old amount before resize. Sound.
- Deposit conservation: `DepositTransLib` checks `processDeposit`'s boolean return (no free-mint); `processWithdraw`
  guards `systemBalance`. Liquidate/Deleverage conserve synthetic + collateral between the two parties. Sound.
- Permissions delegation rule (`PermissionsTransLib` + `SignerManager`): correctly enforces "grant only what you
  hold." `AccountManager.registerAccount` blocks overwrite/takeover (one-address-one-account). Sound.
- `SyntheticPositionLib` packing (accountId/assetId/cpIndex, non-overlapping masks), `Uint64Set` (EnumerableSet
  clone), `EIP712DomainLib` (binds chainId + verifyingContract → no cross-chain/contract replay), `OrderManager`
  fulfillment (monotonic, bounded by signed amount → no over-fill). Sound.

## Bottom line
**Two confirmed High/Critical with passing PoCs** — F-1 (margin bypass on collateral withdrawal, Critical) and F-2
(account freeze / liquidation-lock past the top risk segment, High) — plus the inverted-ratio de-risk DoS (M-1,
PoC'd), the oracle-staleness gap (M-2), the `configVersion` parity bug (M-4), and trust-dependent / minor notes
(M-3, L-1..L-4). One theft lead (negative-amount transfer) was investigated and **disproven** (plugin-level guard).
Four standalone Foundry PoCs in this directory. **Nothing submitted** — the user reviews and submits.
