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
is why it is rated Low/Medium rather than higher — but it defeats a built-in safety mechanism.

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

Steps proven: record `configVersion`; call `setSyntheticAssetsInfo(...)` (change a risk segment) — version is
unchanged. Control: `setMaxFundingRate(...)` — version increments by 1.

Captured output (passes):

```
[PASS] test_PoC_setSyntheticAssetsInfo_doesNotBumpConfigVersion()
  configVersion before setSyntheticAssetsInfo: 2
  configVersion after  setSyntheticAssetsInfo: 2
  configVersion after  setMaxFundingRate     : 3
Suite result: ok. 3 passed; 0 failed; 0 skipped
```

# Field: Attachments
- PoC_ConfigVersionNotBumped.t.sol
- poc_output.log   (captured passing run)
