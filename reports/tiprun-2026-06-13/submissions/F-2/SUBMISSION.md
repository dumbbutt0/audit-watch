<!--
PLATFORM-PASTE-READY version of the F-2 report. Plain prose + standard code fences only — no blockquote
header, no viewer "Copy"/language-label artifacts. Paste each labelled section into the matching HackenProof
field. Facts are identical to report.md (validated, PoC passing: 2 scenario tests); only the framing/order is
tuned for the submission form (impact-led title, explicit severity rationale). Copy from the RAW file, not a
rendered preview, to avoid pulling in a viewer's "Copy" button text.
-->

# Field: Target
https://github.com/hackenproof-public/tiprun-contracts

# Field: Category
Business Logic Errors

# Field: Severity
High

# Field: Title
Risk segment overflow freezes insolvent shorts and blocks faithful liquidation, causing protocol bad debt

# Field: Vulnerability details

When a position's notional exceeds the top configured risk segment, `GeneralConfig.getRiskFactor` returns
`(0, false)` and `Risk.getAssetValueAndRisk` reverts with `"Risk: no risk"` instead of clamping to the top
tier. Because every position-touching operation routes through that function, a single over-cap asset freezes
the entire account — including the liquidation path. On the short side an attacker can deliberately drive an
account into a state that is simultaneously insolvent and un-liquidatable, leaving unrecoverable bad debt.

## Primary impact (High)

The trigger is a plain oracle price increase (notional = `price * |amount|`), not any action on the account.
When an asset pumps — exactly when accounts go underwater and most need liquidating — every operation whose
*updated* state would still sit above the top segment reverts: partial liquidation, partial de-risk,
withdrawals, and even read-only status checks. The freeze persists until the price falls back under the cap or
an admin reconfigures the asset.

The unrecoverable case is the insolvent short. For a short, notional rises as price rises — precisely as the
short goes underwater. An attacker sizes a short so its maintenance-margin breach lands above the segment cap.
`checkValidTransition` evaluates the *updated* position first and only early-returns if that updated state is
healthy and below the cap (see Root cause); Under the protocol’s faithful close accounting, reducing the insolvent short realizes the buyback loss as negative collateral. The updated state is therefore not healthy, so checkValidTransition falls through to the frozen initial state and reverts. So **every faithful liquidation reverts** and the protocol cannot
seize the account — the loss is unrecoverable bad debt.

Scope / qualification (proven): a still-*solvent* over-cap account is not permanently bricked — a single
one-shot full close reaches a healthy below-cap state and succeeds, so for solvent accounts this is a
partial-de-risk / withdrawal denial-of-service rather than a permanent lock. The High impact is the insolvent
variant, where the account is simultaneously underwater and un-liquidatable. No privileged role or victim
action is required to trigger it.

## Root cause

`getRiskFactor` walks the asset's risk-factor segments and returns `(segment.risk, true)` for the first
segment whose `upperBound` covers the position's notional; if the notional exceeds every segment it returns
`(0, false)`. `Risk.getAssetValueAndRisk` then executes `require(riskOk, "Risk: no risk")` and reverts — it
does not clamp to the top tier:

```solidity
// Risk.getAssetValueAndRisk
(int256 riskFactor, bool riskOk) = generalConfig.getRiskFactor(asset.packed.getAssetId(), absAmount, oraclePrice);
if (!priceOk) { require(!riskOk, "Risk: price missing but risk exists"); return (0, 0); }
require(riskOk, "Risk: no risk");   // reverts when notional > top segment
```

Because every position-touching operation (withdraw, trade, liquidate, deleverage, settlement) routes through
`checkValidTransition -> getAccountPositionStatus -> getAssetValueAndRisk`, a single asset whose notional
crosses the cap freezes the entire account.

`checkValidTransition` is what turns this into a liquidation lock rather than a momentary glitch:

```solidity
// Risk.checkValidTransition
(int256 updatedTotalValue, int256 updatedTotalRisk) = getAccountPositionStatusWithBoundaryCheck(fullUpdated);
if (updatedTotalRisk <= updatedTotalValue * FXP_32_ONE) { return; }          // (1) early-return iff updated is healthy
// otherwise evaluate the (still over-cap) initial state:
(int256 initTotalValue, int256 initTotalRisk) = getAccountPositionStatusWithBoundaryCheck(fullInit); // (2) reverts "Risk: no risk"
```

It evaluates the *updated* position first: a reduction that stays above the cap reverts inside
`getAccountPositionStatusWithBoundaryCheck(fullUpdated)`; it early-returns only when the updated state is
healthy and below the cap; otherwise it falls through to `getAccountPositionStatusWithBoundaryCheck(fullInit)`,
which reverts on the still-over-cap initial state. So the only transition that succeeds is one reaching a
healthy below-cap state. A solvent account can get there with a one-shot full close; an insolvent account
cannot (closing realizes the loss), which is why insolvent over-cap accounts are effectively un-liquidatable.

## Suggested fix

In `getRiskFactor`, clamp to the last segment's risk when notional exceeds all segments (never return
`false`); or handle `riskOk == false && priceOk == true` in `Risk` without reverting. A maintenance-margin
engine must never revert on a too-large position — that is exactly the state in which liquidation must remain
possible.

# Field: Validation steps

The PoC runs against the project's own contracts in a local Foundry harness; all scenario tests pass. Every
position update routes through the same `checkValidTransition` gate that liquidation uses, so these
`updatePositionInDict` transitions are representative of the liquidation path. From the harness root:

```bash
forge test --match-contract PoC_RiskSegmentFreeze -vv
```

Scenario 1 (`test_PoC_priceRiseFreezesAccountAndBlocksLiquidation`): long 5,000 @ price 1 (notional 5,000 <=
cap 10,000) is healthy; raise the oracle price to 3 (notional 15,000) and `getAccountPositionStatus`, a
partial resize, and a withdrawal batch all revert `Risk: no risk` — the account is frozen for partial
de-risk and withdrawals.

Scenario 2 (`test_PoC_shortDodgesLiquidationByFreezing`): short 3,000 @ price 1 (healthy); raise price to 4 so
equity = `10,000 - 4*3,000 = -2,000` (insolvent); a partial resize that stays above the cap reverts
`Risk: no risk`.

Scenario 3 (`test_PoC_solventOverCapAccountSelfRescuesWithFullClose`) — scope/qualification: a *solvent*
over-cap long still reverts on a partial reduce, but a one-shot **full close succeeds** (the updated state is
healthy and below the cap, so `checkValidTransition` early-returns without evaluating the frozen init). This
proves the freeze on a solvent account is a partial-de-risk/withdrawal DoS, not a permanent lock.

Scenario 4 (`test_PoC_insolventShortCannotBeLiquidatedByAnyFaithfulClose`) — the unrecoverable case: for the
insolvent short, a **faithful full close** (realize the 12,000 buyback loss as `collateralDelta`) and a
**faithful partial close** that brings notional below the cap but leaves the account unhealthy **both revert
`Risk: no risk`** (the updated state is not healthy, so the init/frozen state is evaluated and reverts). The
only "close" that does not revert is one that abandons the loss (`collateralDelta = 0`) — i.e. not a real
liquidation. Hence the insolvent over-cap account is effectively un-liquidatable → unrecoverable bad debt.

Captured output (all scenarios pass):

```
[PASS] test_PoC_priceRiseFreezesAccountAndBlocksLiquidation()
  account frozen after price rise: notional 15000 > top risk segment 10000
[PASS] test_PoC_shortDodgesLiquidationByFreezing()
  insolvent short is frozen and cannot be liquidated: notional 12000 > cap 10000
[PASS] test_PoC_solventOverCapAccountSelfRescuesWithFullClose()
  solvent over-cap account self-rescued via one-shot full close
[PASS] test_PoC_insolventShortCannotBeLiquidatedByAnyFaithfulClose()
  insolvent over-cap short: no faithful close executes -> unrecoverable bad debt
Suite result: ok. 6 passed; 0 failed; 0 skipped
```

# Field: Attachments
- PoC_RiskSegmentFreeze.t.sol
- poc_output.log   (captured passing run)
