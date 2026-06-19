<!--
PLATFORM-PASTE-READY version of the M-4 report. Plain prose + standard code fences only — no blockquote
header, no viewer "Copy"/language-label artifacts. Paste each labelled section into the matching HackenProof
field. Facts are identical to report.md (validated, PoC passing). Copy from the RAW file, not a rendered
preview.
-->

# Field: Target
https://github.com/hackenproof-public/tiprun-contracts

# Field: Category
Business Logic Errors

# Field: Severity
Low

# Field: Title
setSyntheticAssetsInfo skips the configVersion bump, voiding the stale-config protection for risk/oracle params

# Field: Vulnerability details

`GeneralConfig.setSyntheticAssetsInfo` sets the most security-relevant per-asset config (risk-factor segments,
oracle signer set, oracle quorum, max funding rate, resolution) but its `incrConfigVersionInternal()` call is
commented out — whereas every other mutator bumps the version. Because
`MultiTransactionProcessor.processMultiTransactions` only rejects a batch when `configVersion < currentVersion`,
changing these parameters without bumping the version means in-flight user transactions (signed against the old
config) execute under the new parameters, and the stale-config guard that should protect them never triggers.

## Impact

This is Low/Medium because the config-version safety guarantee is silently void for exactly the config that
most affects margin and oracle trust: a risk-factor or oracle-signer change can take effect on already-submitted
batches without the version-mismatch protection. It is admin-triggered (not an arbitrary-attacker drain), which
is why it is rated Low/Medium rather than higher — but it defeats a built-in safety mechanism, and the harm lands
on users (whose in-flight batches were meant to be protected from mid-flight parameter changes), not on the admin.
The PoC demonstrates the consequence end to end: a user batch carrying the pre-change config version still executes
after a risk-parameter change, whereas the identical batch is correctly rejected after any normal config change.

## Root cause

`setSyntheticAssetsInfo` has its `incrConfigVersionInternal()` commented out, while the sibling setters
(`setCollateralAssetInfo`, `setFeeAccountId`, `setMaxFundingRate`, `removeSyntheticAssetInfo`,
`setIsRiskByBalanceOnly`) all bump the version. The batch guard keys on that version, so it is bypassed for
synthetic-asset config changes.

## Suggested fix

Call `incrConfigVersionInternal()` at the end of `setSyntheticAssetsInfo` to restore parity with the other
setters.

# Field: Validation steps

The PoC runs against the project's own contracts in a local Foundry harness; it passes. From the harness root:

```bash
forge test --match-contract PoC_ConfigVersionNotBumped -vv
```

Steps proven:
- L2 (missing bump): record `configVersion` (= 2); call `setSyntheticAssetsInfo(...)` (change a risk segment) —
  version unchanged (still 2). Control: `setMaxFundingRate(...)` — version increments to 3.
- L3 (guard bypass): a user batch carrying the stale `configVersion = 2` is submitted to
  `MultiTransactionProcessor.processMultiTransactions`. After `setSyntheticAssetsInfo` it is ACCEPTED (the
  stale-config guard never fires). After the version-bumping `setMaxFundingRate`, the same stale batch is REJECTED
  with `"MultiTransactionProcessor: config version mismatch"`. Identical batch, opposite outcome.

Captured output (passes):

```
[PASS] test_PoC_setSyntheticAssetsInfo_doesNotBumpConfigVersion_bypassesStaleGuard()
  configVersion before setSyntheticAssetsInfo: 2
  configVersion after  setSyntheticAssetsInfo: 2
  configVersion after  setMaxFundingRate     : 3
Suite result: ok. 3 passed; 0 failed; 0 skipped
```

# Field: Attachments
- PoC_ConfigVersionNotBumped.t.sol
- poc_output.log   (captured passing run)
