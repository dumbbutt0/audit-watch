<!--
PLATFORM-PASTE-READY version of the N-2 report. Plain prose + standard code fences only. Paste each labelled
section into the matching platform field. Facts are identical to the PoC (validated, all tests passing). Copy from
the RAW file, not a rendered preview.
-->

# Field: Target
https://github.com/hackenproof-public/tiprun-contracts

# Field: Category
Business Logic Errors / Insecure Design

# Field: Severity
High (conditional on perp profile — see scope caveat)

# Field: Title
PositionManager._marginCheck() silently falls back to a no-op when no CAP_MARGIN_CHECK provider is registered, and registerPlugin never requires one, so a perp deployment can accept undercollateralized positions

# Field: Vulnerability details

`PositionManager._marginCheck()` resolves the maintenance-margin enforcer via the capability registry and falls back
to a no-op when no provider is registered:

```solidity
function _marginCheck() internal view returns (IMarginCheck) {
    address provider = ICapabilityRegistry(transactionProcessor).capabilityProvider(CAP_MARGIN_CHECK);
    if (provider == address(0)) return nullMarginCheck;   // no-op fallback
    return IMarginCheckProvider(provider).marginCheck();
}
```

`NullMarginCheck.checkValidTransition` is empty and `getAccountPositionStatus` returns (0,0) — every transition is
"valid." The fallback is intended for spot (no maintenance margin), but nothing forces a real provider on a profile
that needs one. `TransactionProcessor.registerPlugin` only enforces a plugin's declared `requiredCapabilities()`:

```solidity
require(capabilityProvider[required[i]] != address(0), "TransactionProcessor: missing required capability");
```

…and no plugin declares CAP_MARGIN_CHECK as required. So the full trading surface can be registered without a margin
provider, and the safety net is opt-out by omission — the system fails OPEN, not closed.

## Impact

On a perp profile with no (or temporarily no) CAP_MARGIN_CHECK provider, the only maintenance-margin enforcement is
bypassed: undercollateralized positions/withdrawals are accepted -> insolvency / bad debt. A single misconfiguration
(or a deploy/upgrade window, or an unregisterPlugin that clears the provider) silently disables the core solvency
check with no revert and no event.

## Root cause

Safety-critical capability fails open: `_marginCheck()` falls back to NullMarginCheck when the provider is absent, and
`registerPlugin` does not require a CAP_MARGIN_CHECK provider for margin-gated txTypes.

## Suggested fix

Make margin-gated plugins declare CAP_MARGIN_CHECK (and CAP_BALANCE_CHECK) in `requiredCapabilities()` so registration
reverts without a real provider; or make `_marginCheck()` fail-closed for margin-gated profiles.

# Field: Validation steps

The PoC runs against the project's own contracts in a local Foundry harness; all tests pass. From the harness root:

```bash
forge test --match-contract PoC_CapabilityRegistryNoop -vv
```

What it proves:

- `test_PoC_missingMarginProviderAcceptsInsolventPosition`: starting from the base harness (which wires a real
  CAP_MARGIN_CHECK provider), the test reproduces the finding's condition by clearing the provider
  (`unregisterPlugin(riskPlugin)` — never required by registerPlugin), then opens a short of 5000 against 1000
  collateral. With the real margin check this is rejected; with the no-op it is accepted, and the still-deployed Risk
  view confirms the accepted account value is negative (insolvent).

Captured output (real run, all passing):

```
Ran 3 tests for test/PoC_CapabilityRegistryNoop.t.sol:PoC_CapabilityRegistryNoop
[PASS] testResolutionCheck()
[PASS] testSyntheticAssetInfoCRUD()
[PASS] test_PoC_missingMarginProviderAcceptsInsolventPosition()
Logs:
  accepted account value at true price (FXP, negative = insolvent): negative
  synthetic short held with no maintenance-margin enforcement: 5000

Suite result: ok. 3 passed; 0 failed; 0 skipped
```

# Field: Scope caveat (read before submitting)

This has impact only on a deployment that should run the perp Risk margin engine but does not have it registered. On
a spot/predict profile the no-op fallback is intended (no maintenance margin) and there is no impact — the same
not-wired condition under which the related risk-segment finding was ruled out of scope. Submit only if the perp
margin profile is in scope for the target deployment; otherwise this is a design/hardening note (fail-open vs
fail-closed).

# Field: Attachments
- PoC_CapabilityRegistryNoop.t.sol
- poc_output.log   (captured passing run)
