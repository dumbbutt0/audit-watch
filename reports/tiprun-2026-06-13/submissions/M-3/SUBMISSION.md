<!--
PLATFORM-PASTE-READY version of the M-3 report. Plain prose + standard code fences only — no blockquote
header, no viewer "Copy"/language-label artifacts. Paste each labelled section into the matching HackenProof
field. Facts are identical to report.md (validated, PoC passing). This is a trust-dependent (operator)
finding — stated honestly. Copy from the RAW file, not a rendered preview.
-->

# Field: Target
https://github.com/hackenproof-public/tiprun-contracts

# Field: Category
Business Logic Errors

# Field: Severity
Medium

# Field: Title
Liquidate/Deleverage can seize perfectly healthy accounts — no on-chain maintenance-margin precondition

# Field: Vulnerability details

`LiquidateTransLib.process` never checks that the targeted account is below maintenance margin before
force-resizing its position, and `DeleverageTransLib.process` checks only that both parties are registered
signers (no signature, no nonce, no health precondition). Both are gated by `onlyTxBatcher`, so the on-chain
contract trusts the off-chain risk engine entirely: there is no on-chain guarantee that "only unhealthy
accounts can be liquidated/deleveraged."

## Impact

A faulty or malicious sequencer can force-trade or seize positions of perfectly healthy, fully-collateralized
accounts at an operator-chosen price. Combined with F-1 (the margin check does not block value-reducing
transitions on the liquidated account), over-seizure is not blocked either.

This is Medium because exploitation requires the privileged batcher (a trust/centralisation dependency) rather
than an arbitrary attacker; it is Low if the sequencer is considered fully trusted, and higher if users are
meant to be protected on-chain from having healthy positions seized. The missing on-chain safety invariant is
the substance of the report.

Scope caveat (deployment reachability, stated honestly): `LiquidateTransLib` and `DeleverageTransLib` live in
`src/perp/transactions/` and resize positions through `PositionManager.updatePosition -> _marginCheck()`. The
perp margin engine is the `CAP_MARGIN_CHECK` capability provider; when it is not registered, `_marginCheck()`
falls back to `NullMarginCheck` (a no-op) and there is no perp risk/liquidation engine at all. So this finding is
in scope only on a deployment that wires the perp `Risk` engine. If the in-scope deployment runs the predict/spot
profile with `NullMarginCheck` — the same not-wired condition under which the related risk-segment finding was
ruled out of scope — liquidation/deleverage are not active and this finding is out of scope for the same reason.
The single deciding fact is whether `CAP_MARGIN_CHECK` is wired to the real `Risk` engine in the target
deployment; confirm that before submitting.

## Root cause

`LiquidateTransLib.process` computes deltas, applies funding, and calls `position.updatePosition(...)` plus the
liquidator order, with no `require(account is unhealthy)`. `DeleverageTransLib.process` is weaker still: it
only calls `signerManager.checkSigner(...)` for both parties — no signature, no nonce, no health precondition —
so the operator can force any account to be the deleverager or the deleveraged.

## Suggested fix

Require the target to be below maintenance margin before liquidation/deleverage (compute health on-chain and
revert otherwise), and bound the liquidation price to oracle +/- a configured penalty. For deleverage, require
a real signature/consent model or an explicit bankrupt-state precondition.

# Field: Validation steps

The PoC runs against the project's own contracts in a local Foundry harness; it passes (alongside the repo's
existing liquidate tests, all green). From the harness root:

```bash
forge test --match-contract PoC_NoLiquidatablePrecondition -vv
```

Steps proven: the target holds 100 collateral and a tiny long of 1 — proven healthy (`risk <= value*FXP`). A
`TYPE_LIQUIDATE` transaction liquidates it anyway: the position is force-closed (`assets.length == 0`) and the
forced trade settles against the target — no "not liquidatable" guard fires.

Captured output (passes; the key case shown):

```
[PASS] test_PoC_canLiquidatePerfectlyHealthyAccount()
  healthy target value (FXP): 433791696896
  healthy target risk  (FXP^2): 18446744073709551616
  liquidated despite being healthy: position length now 0
Suite result: ok. 25 passed; 0 failed; 0 skipped
```

# Field: Attachments
- PoC_NoLiquidatablePrecondition.t.sol
- poc_output.log   (captured passing run)
