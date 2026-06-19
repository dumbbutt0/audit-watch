<!--
PLATFORM-PASTE-READY version of the N-4 report. Plain prose + standard code fences only. Paste each labelled
section into the matching platform field. Facts are identical to the PoC (validated, all tests passing). Copy from
the RAW file, not a rendered preview.
-->

# Field: Target
https://github.com/hackenproof-public/tiprun-contracts

# Field: Category
Business Logic Errors

# Field: Severity
Low (operator-trust-gated — missing on-chain invariant)

# Field: Title
SettlementTransLib.process credits collateral = syntheticBalance * settlementPrice with no oracle binding, no signed-outcome binding, and no aggregate conservation invariant, so a mis-priced settlement mints unbacked withdrawable collateral

# Field: Vulnerability details

`SettlementTransLib.process` force-settles a synthetic position and credits collateral equal to
`syntheticBalance * settlementPrice`, where `settlementPrice` is a raw operator input bounded only by
`[0, int128.max]`:

```solidity
require(self.settlementPrice >= 0 && self.settlementPrice <= type(int128).max, "SettlementTransLib: invalid settlement price");
int256 syntheticBalance = position.getSyntheticBalance(self.accountId, self.syntheticAssetId);
if (syntheticBalance == 0) { return; }
int256 collateralDelta = syntheticBalance * self.settlementPrice;
int256 syntheticDelta  = -syntheticBalance;
position.updatePositionInDict(self.accountId, collateralDelta, self.syntheticAssetId, syntheticDelta);
```

There is no oracle binding (price not checked against `Oracle.getPrice`), no signature/outcome binding, and no
aggregate YES/NO conservation invariant (nothing checks that collateral credited to winners equals collateral burned
from losers or is backed by `LoadingZone` reserves). The operator can settle any position at any price.

## Impact

Operator-mispriced or one-sided settlement mints collateral not offset by a matching burn and not backed by reserves;
the unbacked collateral becomes withdrawable, allowing a later withdrawal to drain other users' deposited tokens.
Bounded only by operator honesty — no on-chain invariant caps or conserves settlement payouts. Gated by operator
trust, so no permissionless exploit (reported Low / missing-invariant).

## Root cause

`settlementPrice` is unconstrained operator input; settlement payout is not bound to oracle/outcome and there is no
aggregate conservation check.

## Suggested fix

Bind `settlementPrice` to a signed resolution outcome and/or the asset oracle price; enforce a per-market
conservation invariant (credited <= burned + available reserves).

# Field: Validation steps

The PoC runs against the project's own contracts in a local Foundry harness; all tests pass. From the harness root:

```bash
forge test --match-contract PoC_SettlementUnconstrained -vv
```

What it proves:

- `test_PoC_settlementMintsUnbackedCollateralAtOperatorPrice`: an account holds synthetic 100, oracle price 1; the
  operator settles at an arbitrary price of 50 (unrelated to the oracle, no signature/oracle check). The synthetic is
  zeroed and collateral is credited by exactly balance * operatorPrice = 5000 — unbacked, later-withdrawable
  collateral minted from an operator-chosen number.

Captured output (real run, all passing):

```
Ran 3 tests for test/PoC_SettlementUnconstrained.t.sol:PoC_SettlementUnconstrained
[PASS] testResolutionCheck()
[PASS] testSyntheticAssetInfoCRUD()
[PASS] test_PoC_settlementMintsUnbackedCollateralAtOperatorPrice()
Logs:
  oracle price (FXP): 4294967296
  operator settlement price used: 50
  unbacked collateral minted: 5000

Suite result: ok. 3 passed; 0 failed; 0 skipped
```

# Field: Scope caveat (read before submitting)

Settlement is operator-driven; on a deployment with a fully trusted, off-chain-audited operator, programs may treat
this as accepted design ("relies on trusted operator"). Submit as a missing on-chain invariant / defense-in-depth
finding and state the trust dependency explicitly.

# Field: Attachments
- PoC_SettlementUnconstrained.t.sol
- poc_output.log   (captured passing run)
