# N-2 (High) — Capability registry silently falls back to a no-op margin check when no provider is registered

- **Target:** TipRun contracts (off-chain-match / on-chain-settlement exchange). Commit `d5d4d2a…`.
- **Contract:** `src/core/position/PositionManager.sol` → `_marginCheck()`, with the registration logic in
  `src/TransactionProcessor.sol` → `registerPlugin` and the no-op fallback `src/core/risk/NullMarginCheck.sol`
  (capability constant in `src/Constants.sol`).
- **Severity:** High (undercollateralized positions / withdrawals silently accepted → protocol insolvency / bad
  debt) **on a perp profile where the margin engine is not wired**. See the scope caveat — this is a fail-open
  design, not a defect reachable on every deployment.
- **PoC (passing):** `poc/PoC_CapabilityRegistryNoop.t.sol` · log `poc_output.log`.
- **Actor:** anyone acting on a deployment whose `CAP_MARGIN_CHECK` provider is missing or temporarily unregistered.

## Root cause
`PositionManager._marginCheck()` resolves the maintenance-margin enforcer through the capability registry and
**falls back to a no-op** when no provider is registered:

```solidity
// PositionManager._marginCheck()
function _marginCheck() internal view returns (IMarginCheck) {
    address provider = ICapabilityRegistry(transactionProcessor).capabilityProvider(CAP_MARGIN_CHECK);
    if (provider == address(0)) return nullMarginCheck;   // <-- no-op fallback
    return IMarginCheckProvider(provider).marginCheck();
}
```

`NullMarginCheck.checkValidTransition` is an empty function and `getAccountPositionStatus` returns `(0, 0)` — every
transition is "valid" by definition. The fallback exists intentionally for spot deployments (no maintenance margin).
The problem is that **nothing forces a real provider to exist on a profile that *does* need one.**

`TransactionProcessor.registerPlugin` enforces a plugin's *declared* `requiredCapabilities()`:

```solidity
for (uint256 i = 0; i < required.length;) {
    require(capabilityProvider[required[i]] != address(0), "TransactionProcessor: missing required capability");
    ...
}
```

…but **no plugin declares `CAP_MARGIN_CHECK` as a required capability.** The position/trade plugins that mutate
collateral and synthetics never list it in `requiredCapabilities()`, so a deployment can register the full trading
surface without ever wiring a `CAP_MARGIN_CHECK` provider. The safety net is therefore **opt-out by omission**: if
the operator forgets to register the perp `Risk` provider (or during a pre-wiring window, or after an
`unregisterPlugin` that clears it), margin checks become a silent no-op and the system fails *open*, not closed.

## Impact
On a perp profile with no (or temporarily no) `CAP_MARGIN_CHECK` provider, the only maintenance-margin enforcement is
bypassed: undercollateralized positions and collateral withdrawals are accepted unconditionally → protocol
insolvency / bad debt borne by other users. Because there is no on-chain assertion that a margin provider exists for
margin-gated transaction types, a single misconfiguration (or a window during deploy/upgrade) silently disables the
core solvency guarantee with no revert and no event signalling that checks are off.

## PoC (passing)
From `../../harness/`:

```bash
forge test --match-contract PoC_CapabilityRegistryNoop -vv
```

`test_PoC_missingMarginProviderAcceptsInsolventPosition`: starting from the base harness (which *does* wire a real
`CAP_MARGIN_CHECK` provider), the test reproduces the finding's condition by clearing that provider — it calls
`unregisterPlugin(riskPlugin)`, which `registerPlugin` never required, leaving `capabilityProvider(CAP_MARGIN_CHECK)
== address(0)`. It then opens a short of 5000 against only 1000 collateral. With the real Risk margin check this is
rejected; with the `NullMarginCheck` no-op it is **accepted**, and the still-deployed Risk contract (used only as a
view) confirms the accepted account value is negative (insolvent). See `poc_output.log`.

## Suggested fix
- Enforce required capability providers at `registerPlugin`: a plugin supporting margin-gated `txTypes` must declare
  `CAP_MARGIN_CHECK` (and `CAP_BALANCE_CHECK`) in `requiredCapabilities()` so registration reverts unless a real
  provider is wired.
- Alternatively, make `_marginCheck()` fail-closed for margin-gated profiles: only fall back to `NullMarginCheck` for
  explicitly spot-configured deployments, and revert when a margin-gated txType is processed with no real provider.

## Submission caveats (honest — verify before submitting)
- **Deployment reachability (the deciding factor):** this only has impact on a deployment that *should* run the perp
  `Risk` margin engine but doesn't have it registered. On the live predict/spot profile the no-op fallback is the
  intended behavior (no maintenance margin) and there is no impact — this is the same not-wired condition under which
  the F-2 risk-segment finding was ruled out of scope. Confirm the target deployment runs the perp margin profile
  and the conditions under which `CAP_MARGIN_CHECK` could be absent (deploy window, upgrade, operator error) before
  claiming impact. As a pure design/hardening note (fail-open instead of fail-closed) it stands regardless.
- **Novelty:** verify against prior TipRun audits that the fail-open capability fallback is not already reported.

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Business Logic Errors / Insecure Design — safety-critical check fails open (no-op fallback)
  when a capability provider is unregistered, with no registration-time enforcement.
- **CWE (informative):** CWE-636 (Not Failing Securely / "Failing Open"); CWE-840 (Business Logic Errors).

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| Margin check silently no-op on a misconfigured perp profile | `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:H` | **6.4** | Medium–High |

> Severity is conditional on the deployment profile (perp margin engine expected but unwired). On a spot/predict
> profile the fallback is intended and there is no impact. Protocol/bounty severity may differ from the CVSS band.

<!-- END classification-cvss -->
