<!--
PLATFORM-PASTE-READY version of the M-2 report. Plain prose + standard code fences only — no blockquote
header, no viewer "Copy"/language-label artifacts. Paste each labelled section into the matching HackenProof
field. Facts are identical to the PoC (validated, all tests passing). Copy from the RAW file, not a rendered
preview, to avoid pulling in a viewer's "Copy" button text.
-->

# Field: Target
https://github.com/hackenproof-public/tiprun-contracts

# Field: Category
Business Logic Errors

# Field: Severity
Low

# Field: Title
Oracle has no read-side staleness/max-age and the monotonic-update guard is removed, so the trusted update flow can store a stale or rolled-back price that margin and liquidation then trust indefinitely

# Field: Vulnerability details

The Oracle has two missing recency guards that, together, give the system no defense-in-depth if a stale or
out-of-order price is ever stored:

1. `Oracle.updatePrice` has its monotonic-timestamp guard commented out (`Oracle.sol`), so the stored price can
   regress to an older timestamp.
2. `Oracle.getPrice` returns `exist = (timestamp > 0)` with no max-age, and `Risk.getAssetValueAndRisk` consumes
   that price with no staleness check. Once a price is stored it is used by every margin and liquidation decision
   forever.

Trust model (stated up front, because it bounds the severity): this is NOT reachable by an unprivileged user.
Every write path into the Oracle is privileged — `Oracle.updatePrice` is `onlyAuthorizedCaller` (a registered
plugin or the owner), and the batch route is `MultiTransactionProcessor.processMultiTransactions`
(`onlyTxBatcher`) -> `TransactionProcessor` (`onlyMultiTransactionProcessor`) -> `OraclePlugin`
(`onlyTransactionProcessor`). The repo's own test `TransactionProcessor.basic.t.sol::testOracleRejectsUnauthorizedCaller`
confirms a plain EOA reverts. So the realistic trigger is the trusted update flow itself delivering a stale or
reordered price — operator delay, a chain reorg, or a backend retry that re-applies a recently-signed (<= 1-day,
still passing the ingestion freshness bound in `OraclePriceTickTransLib`) tick out of order. No malicious actor
is required; the issue is the absence of a guard, not an exploit primitive.

## Impact

Reported as Low (defense-in-depth / robustness). It is not an unprivileged drain and there is no attacker
primitive — but solvency-critical math (margin checks, liquidations) has no on-chain guarantee that the price it
uses is recent, and a regressed/stale price flips real solvency decisions. The PoC demonstrates the downstream
consequence end to end: an account that is INSOLVENT at the true price reads as solvent and healthy after the
price is rolled back, so its liquidation is hidden and a margin/withdraw check would pass. The condition for harm
(the trusted feed actually being stale or reordered) is what keeps this conditional rather than a guaranteed loss.

Scope caveat (stated honestly): the ONLY consumer of `oracle.getPrice` is `Risk.getAssetValueAndRisk`, which is
reached only via `PositionManager._marginCheck()` → the `CAP_MARGIN_CHECK` provider. That capability is perp-only
(`Constants.sol`); when it is not registered, `_marginCheck()` falls back to `NullMarginCheck` (a no-op that never
reads the oracle). So the margin/liquidation impact above only materializes on a deployment where the perp `Risk`
margin engine is actually wired. If the in-scope deployment runs the predict/spot profile with `NullMarginCheck`
(the same not-wired condition under which the related risk-segment finding was ruled out of scope), nothing live
reads the oracle price and this reduces to a code-quality / hardening note with no value impact. Submit only if
the perp margin check is in scope for the target deployment.

## Root cause

`Oracle.updatePrice` has its `timestamp > current` monotonic guard commented out (a `TODO`); `Oracle.getPrice`
returns `exist = (timestamp > 0)` with no freshness/max-age check; and `Risk.getAssetValueAndRisk` consumes the
price without any staleness check. The only recency check in the system, `OraclePriceTickTransLib`'s `<= 1-day`
ingestion bound, guards the update transaction, not the read — and its own monotonic check is also commented out,
so a newer-then-older ordering within the 1-day window is accepted.

## Suggested fix

Restore the monotonic timestamp guard in `Oracle.updatePrice` (and in `OraclePriceTickTransLib._validatePrice`),
and enforce a max-age on read in `Oracle.getPrice` (or in `Risk` before the price is used), so margin and
liquidation revert or flag when the price backing a solvency decision is stale.

# Field: Validation steps

The PoC runs against the project's own contracts in a local Foundry harness; all tests pass. From the harness
root:

```bash
forge test --match-contract PoC_OracleStaleness -vv
```

What it proves (the actor is the price-update authority, modelled with `vm.prank(deployer)`, since the path is
privileged):

- `test_PoC_authorityCanRollPriceBackAndItNeverExpires`: set price 100 at a recent timestamp; call `updatePrice`
  with an older timestamp and price 1 — accepted (no monotonic guard), and `getCurrentTimestamp` regresses.
  Advance ~10 years; `getPrice` still reports `exist = true` for the now-ancient price (no read-side max-age). The
  test asserts the advance actually happened and that the stored price is >= 3650 days old yet still valid.
- `test_PoC_stalePriceFlipsSolvencyAndHidesLiquidation`: open a short that is healthy at price 1; raise the true
  price so the account is insolvent (account value < 0) while staying below the risk-segment cap; then roll the
  price back to the old value. `Risk.getAccountPositionStatus` now reports the same position as solvent and
  healthy — liquidation is hidden and a margin check would pass on the stale price.

Captured output (real run, all passing):

```
Ran 4 tests for test/PoC_OracleStaleness.t.sol:PoC_OracleStaleness
[PASS] testResolutionCheck() (gas: 19826)
[PASS] testSyntheticAssetInfoCRUD() (gas: 84311)
[PASS] test_PoC_authorityCanRollPriceBackAndItNeverExpires() (gas: 62036)
Logs:
  rolled-back price (FXP): 4294967296
  age of stored price at read (days): 3650

[PASS] test_PoC_stalePriceFlipsSolvencyAndHidesLiquidation() (gas: 413584)
Logs:
  account value at TRUE price (insolvent, <0): negative
  account value at STALE price (looks healthy): 8589934592000

Suite result: ok. 4 passed; 0 failed; 0 skipped
```

# Field: Attachments
- PoC_OracleStaleness.t.sol
- poc_output.log   (captured passing run)
