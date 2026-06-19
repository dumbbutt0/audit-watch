# M-4 (Medium/Low) — `setSyntheticAssetsInfo` does not bump `configVersion`, defeating the stale-config batch guard

- **Target:** TipRun. Commit `d5d4d2a…`.
- **Contract:** `src/core/config/GeneralConfig.sol` → `setSyntheticAssetsInfo` (the `incrConfigVersionInternal()`
  call is commented out, ~lines 179-182).
- **Severity:** Medium / Low (admin-triggered; undermines a built-in safety mechanism).
- **PoC:** `poc/PoC_ConfigVersionNotBumped.t.sol` (passing — proves the missing bump **and** the resulting
  stale-config-guard bypass) · log `poc_output.log`.

## Root cause
`setSyntheticAssetsInfo` sets the most security-relevant per-asset config — risk-factor segments, oracle signer set,
oracle quorum, max funding rate, resolution — but its `incrConfigVersionInternal()` is commented out, whereas every
other mutator (`setCollateralAssetInfo`, `setFeeAccountId`, `setMaxFundingRate`, `removeSyntheticAssetInfo`,
`setIsRiskByBalanceOnly`) bumps the version.

`MultiTransactionProcessor.processMultiTransactions` reverts a batch only when `configVersion < currentVersion`. So
changing risk parameters / oracle signers / quorum without bumping the version means in-flight user transactions
(signed against the old config) execute under the **new** parameters, and the stale-config guard that is supposed to
protect them never triggers.

## Impact
The config-version safety guarantee is silently void for exactly the config that most affects margin and oracle
trust. A risk-factor or oracle-signer change can take effect on already-submitted batches without the version-mismatch
protection.

## PoC (passing)
`forge test --match-contract PoC_ConfigVersionNotBumped -vv` (from `../../harness/`). The PoC proves both the missing
bump (L2) and the resulting guard bypass (L3):
- **L2 — missing bump:** record `configVersion` (= 2); call `setSyntheticAssetsInfo(...)` to change the risk segment →
  version **unchanged** (still 2). Control: `setMaxFundingRate(...)` → version **increments** (→ 3).
- **L3 — stale-config guard bypassed:** a user batch carrying the **stale** `configVersion = 2` is submitted through
  the real `MultiTransactionProcessor` relay path. **After `setSyntheticAssetsInfo` it is accepted** (the guard never
  fires, so the batch executes under the new risk params). After the version-bumping `setMaxFundingRate`, the **same
  stale batch is rejected** (`"MultiTransactionProcessor: config version mismatch"`). Identical batch, opposite
  outcome — proving the protection exists for normal config changes and is silently missing for the most
  security-critical one.

## Suggested fix
Call `incrConfigVersionInternal()` at the end of `setSyntheticAssetsInfo` (restore parity with the other setters).

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Business Logic Errors (`setSyntheticAssetsInfo` does not bump `configVersion`; signature/cache validation keyed on the version can pass against stale config)
- **CWE (informative):** CWE-840 (Business Logic Errors); CWE-1265 (Unintended Reentrancy/stale-state — informative)

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| Missing config-version increment | `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:N` | **2.2** | Low |

> PR:H (admin config mutation) + AC:H (requires a consumer relying on the version).

> CVSS v3.1 base scores computed with the official formula (no temporal/environmental modifiers). For smart-contract findings the protocol/bounty severity may differ from the CVSS band; both are stated where they diverge.

<!-- END classification-cvss -->
