<!--
PLATFORM-PASTE-READY version of the F-1 (+M-1) report. Plain prose + standard code fences only — no
blockquote header, no viewer "Copy"/language-label artifacts. Paste each labelled section into the matching
HackenProof field. Facts are identical to report.md (validated, both PoCs passing); only the framing/order
is tuned for the submission form (impact-led title, F-1 first, M-1 secondary, explicit severity rationale).
-->

# Field: Target
https://github.com/hackenproof-public/tiprun-contracts

# Field: Category
Business Logic Errors

# Field: Severity
Critical

# Field: Title
Inverted `Risk.checkValidTransition` guard lets any user withdraw 100% of collateral while a position stays open → protocol bad debt

# Field: Vulnerability details

A single defect in `Risk.checkValidTransition` (the only on-chain maintenance-margin enforcement on a perp
deployment) lets any user with an open position withdraw their entire collateral while the position remains
open and unbacked, leaving unrecoverable bad debt for the protocol/counterparties.

The root cause is one inverted comparison: the value/risk ratio guard at `Risk.sol:133` is reversed, and the
only value-decrease backstop is gated on `initTotalRisk == 0`, so it never runs once an account holds a
position. The same inverted comparison also produces a secondary liveness issue (an under-margined account
cannot partially de-risk) — described at the end as Manifestation B. One fix closes both.

## Primary impact (Critical) — collateral-withdrawal bypass

A user can: deposit collateral, open a leveraged position, then withdraw 100% of their collateral through the
normal signed-withdrawal flow while the position remains open. The withdrawal succeeds even though the account
is left under maintenance margin. The attacker keeps full directional exposure financed entirely by the
protocol (a free option): if the position wins they collect; if it loses they have already removed all margin,
so the loss is unrecoverable bad debt borne by the protocol and counterparties. This breaks the core solvency
invariant of the exchange.

This is Critical because the attacker removes collateral from custody while retaining open directional
exposure, with no privileged role and no victim interaction — losses are socialized to the protocol or
counterparties whenever the position moves against them.

Reachability note (severity is contingent on one wiring fact): `checkValidTransition` runs only when the perp
`Risk` engine is the registered `CAP_MARGIN_CHECK` provider; when it is not, `PositionManager._marginCheck()`
falls back to `NullMarginCheck` (a no-op) and there is no maintenance margin to bypass. So this Critical assumes
the in-scope deployment wires the perp `Risk` margin engine. The related risk-segment finding was ruled out of
scope on the grounds that the live deployment runs predict/spot with `NullMarginCheck` (perp not wired) — if that
same wiring applies here, this finding faces the same reachability objection; if instead the perp engine is in
scope (as accepting this report implies), the perp oracle-staleness and liquidation findings should be treated as
in scope for the same reason. The single deciding fact for all of them is whether `CAP_MARGIN_CHECK` points at the
real `Risk` engine in the target deployment — worth confirming/aligning so the perp findings are triaged
consistently.

## Root cause

`checkValidTransition` is meant to enforce maintenance margin: a position/collateral change is allowed only if
the updated account is healthy, or (if already unhealthy) strictly improves. The relevant logic:

```solidity
// Risk.sol (checkValidTransition)
if (updatedTotalRisk <= updatedTotalValue * FXP_32_ONE) { return; }            // (A) healthy -> allow
...
checkSmallerInSyntheticHoldings(fullInit, fullUpdated);                         // (B) positions may only shrink
if (initTotalValue * updatedTotalRisk < updatedTotalValue * initTotalRisk) {    // (C) ratio guard - INVERTED
    revert("PM: val/risk dec");
}
if (initTotalRisk == 0) {                                                       // (D) value-decrease guard...
    if (updatedTotalValue < initTotalValue) { revert("PM: val dec"); }          //     ...ONLY when risk == 0 (dead)
}
```

Health is `value/risk` (higher = healthier; the account is healthy iff `risk <= value*FXP`). Guard (C) is
supposed to reject transitions that lower that ratio. As written it does the opposite: it reverts when the
updated ratio rises (`initValue*updatedRisk < updatedValue*initRisk`, i.e. `updatedRatio > initRatio`) and
passes when the ratio falls. The only backstop that could have caught a value drop, (D), is gated on
`initTotalRisk == 0`, so it never runs once an account holds a position (`R > 0`).

For a pure collateral withdrawal the synthetic holdings are unchanged, so `updatedRisk == initRisk == R`.
Substituting into (C): `initValue*R < updatedValue*R`, i.e. `initValue < updatedValue`. Removing collateral
makes `updatedValue < initValue`, so (C) is false (no revert) and (D) is skipped because `R > 0`. Net: any
account holding a position can decrease its collateral with no margin check ever reverting — down to zero, or
into negative equity.

The project's own `test/PositionManager.Risk.t.sol::test_ArithmeticEdgeCase_NegativeCollateral` documents the
bypass — comment: "First create a synthetic position to avoid the totalValue decrease restriction."

## Suggested fix

One change to `checkValidTransition`:
- correct the ratio comparison so it reverts when the updated value/risk ratio decreases (account gets less
  healthy), with explicit handling of negative `totalValue`; and
- apply the health-non-worsening / value-non-decrease guard unconditionally (not only when `initRisk == 0`).

Also make `Risk.validateWithdrawal` account for open-position risk, not just raw bucket-0 collateral.

## Secondary manifestation (liveness) — same root cause

The same inverted comparison blocks legitimate recovery: an under-margined account that tries to reduce its
position (the legitimate way to recover) passes (B) (holdings shrank), then hits (C) with `updatedRatio >
initRatio` (it got healthier) and reverts `PM: val/risk dec`, unless it can close enough in one step to become
fully healthy. With partial orderbook fills (the norm), such accounts cannot recover incrementally. The
project's own `test_RiskRatioComparisonLogic` computes `ratioImproved = initRisk*updatedValue >
updatedRisk*initValue`, which is algebraically the (C) revert condition — i.e. the contract reverts exactly
when the ratio improves. The single fix above closes this too.

# Field: Validation steps

Both PoCs run against the project's own contracts in a local Foundry harness and pass. From the harness root:

```bash
forge test --match-contract PoC_MarginBypassWithdraw -vv   # primary: collateral-withdrawal bypass
forge test --match-contract PoC_DeriskDoS -vv              # secondary: de-risk liveness
```

Primary (PoC_MarginBypassWithdraw): deposit 10,000 collateral; risk factor 2x; oracle price 1; open long
5,000 (value 15,000*FXP, risk 10,000*FXP^2 = healthy). Submit a signed Withdrawal for the full 10,000 via
MultiTransactionProcessor; it succeeds. After: collateral 0, position still long 5,000, risk > value*FXP
(under maintenance margin), 10,000 tokens transferred out to the attacker.

Captured output (both suites pass):

```
[PASS] test_PoC_withdrawAllCollateralWhileHoldingPosition()
  value before (FXP): 64424509440000
  value after  (FXP): 21474836480000
  risk before (FXP^2): 184467440737095516160000
  risk after  (FXP^2): 184467440737095516160000
  tokens extracted: 10000
Suite result: ok. 3 passed; 0 failed; 0 skipped

[PASS] test_PoC_cannotPartiallyDeriskUnhealthyAccount()
  under-margin value (FXP): 30064771072000
  under-margin risk (FXP^2): 184467440737095516160000
Suite result: ok. 3 passed; 0 failed; 0 skipped
```

Secondary (PoC_DeriskDoS): reach an under-margin account (collateral 2,000 / long 5,000 => value 7,000*FXP,
risk 10,000*FXP^2) via the primary bug. A fair partial de-risk — sell 500 synthetic for 500 collateral
(value-neutral, risk down to 9,000*FXP^2, strictly healthier but still under margin) — reverts
`PM: val/risk dec`; the position is left untouched. Only a de-risk large enough to reach full health in one
step (sell 4,000) is allowed.

# Field: Attachments
- PoC_MarginBypassWithdraw.t.sol
- PoC_DeriskDoS.t.sol
- poc_output.log   (captured passing run of both suites)
