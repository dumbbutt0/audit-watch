# N-2 (Medium) — Perp margin checks fail open when `CAP_MARGIN_CHECK` is absent, allowing insolvent trades if the Risk provider is not registered

- **Target:** TipRun contracts (off-chain-match / on-chain-settlement exchange). Commit `d5d4d2a…`.
- **Contract:** `src/core/position/PositionManager.sol` → `_marginCheck()`, with the registration logic in
  `src/TransactionProcessor.sol` → `registerPlugin`, the unconstrained trade plugin
  `src/orderbook/plugins/OrderbookPlugin.sol`, and the no-op fallback `src/core/risk/NullMarginCheck.sol`
  (capability constant in `src/Constants.sol`).
- **Severity:** **Medium** as written (fail-open design; a normal user trade opens an under-margin position →
  bad debt **when the perp `Risk` provider is absent**). **High** *only if* a real in-scope perp deployment can
  reach the missing-provider state (deploy/upgrade window, or a perp profile that omits the provider). Likely
  **out of scope** if the only way to reach it is the owner forgetting to / un-registering Risk. See the
  reachability section — the impact is gated entirely on whether the missing-provider state is in scope.
- **PoC (passing — all via the real user path):** `poc/PoC_CapabilityRegistryNoop.t.sol` · log `poc_output.log`.
- **Actor:** an ordinary user submitting a normal signed trade, on a deployment whose `CAP_MARGIN_CHECK` provider
  is absent. (No attacker privilege; the attack action is a relayed `TYPE_TRADE`, not an owner call.)

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

…but **no plugin declares `CAP_MARGIN_CHECK` as a required capability.** In particular the `TYPE_TRADE` handler
`OrderbookPlugin` does not override `requiredCapabilities()`, so it inherits `BasePlugin`'s empty default — PoC test
(1) reads this from the live registry (`requiredCapabilities().length == 0`). A deployment can therefore register the
full trading surface without ever wiring a `CAP_MARGIN_CHECK` provider. The safety net is **opt-out by omission**: if
the perp `Risk` provider is not registered (a pre-wiring window, or a profile that omits it), margin checks become a
silent no-op and the system fails *open*, not closed.

## Impact
On a perp profile with no `CAP_MARGIN_CHECK` provider, the only maintenance-margin enforcement is bypassed: a normal
user-signed trade that the real `Risk` check would reject is **accepted**, opening a position far below maintenance
margin → bad debt the protocol absorbs. The PoC proves this through the **ordinary user path** (a relayed,
user-signed `TYPE_TRADE`), not an owner call: with the provider wired the trade reverts `"PM: risk inc"`; with it
absent the identical trade is accepted, leaving the account at maintenance-risk `9.2e22` against value `4.3e9`
(i.e. risk ≫ value·FXP).

Scope of the proven claim: the PoC demonstrates **position opening** (insolvent trade accepted). It does **not**
separately prove a withdrawal/drain path, so this report does not claim collateral exfiltration — only the
acceptance of an under-margin position (bad-debt creation).

## PoCs (passing — all via the real user path)
From `../../harness/`:

```bash
forge test --match-contract PoC_CapabilityRegistryNoop -vv
```

1. **`test_PoC_tradePluginDoesNotRequireMarginCapability`** — reads the live registry: the `TYPE_TRADE` plugin
   (`OrderbookPlugin`) declares **zero** required capabilities, so `registerPlugin` accepts the trading surface with
   no `CAP_MARGIN_CHECK` provider. (The missing-provider state is reachable by ordinary deployment omission.)
2. **`test_sameUserTradeRevertsWhenRiskProviderRegistered`** (negative control) — with the real `Risk` provider
   wired, a normal signed trade routed through the txBatcher → `MultiTransactionProcessor` → `OrderbookPlugin` →
   `PositionManager.updatePosition` is **rejected** with `"PM: risk inc"`. This proves the margin check — not the
   harness — is the only thing standing between accept and reject.
3. **`test_PoC_userTradeAcceptedWhenPerpMarginProviderMissing`** — the deployment is modelled with the provider
   absent (an owner action, used **only** to set up the misconfigured state — *not* the attack action). The
   **identical, normal user-signed trade** is then **accepted**, leaving the account grossly below maintenance
   margin (`risk > value·FXP`). The attack action is the relayed `TYPE_TRADE`, exactly the path a real user uses.

See `poc_output.log`.

## Suggested fix
- Enforce required capability providers at `registerPlugin`: a plugin supporting margin-gated `txTypes` must declare
  `CAP_MARGIN_CHECK` (and `CAP_BALANCE_CHECK`) in `requiredCapabilities()` so registration reverts unless a real
  provider is wired.
- Alternatively, make `_marginCheck()` fail-closed for margin-gated profiles: only fall back to `NullMarginCheck` for
  explicitly spot-configured deployments, and revert when a margin-gated txType is processed with no real provider.

## Reachability — the deciding factor (honest tri-state)
The attack action is now a normal user trade and the negative control + capability-evidence tests remove any "the
harness manufactured it" objection. What remains genuinely uncertain is **whether the missing-provider state is in
scope** for the target deployment:
- **High** if a real in-scope perp deployment can reach `CAP_MARGIN_CHECK == address(0)` while trading is live — e.g.
  a deploy/upgrade ordering window where `OrderbookPlugin` is registered before/without `RiskPlugin`, or a perp
  profile that omits the provider. Then ordinary user trades create bad debt with no margin enforcement.
- **Medium** as a fail-open design defect: the system has no on-chain assertion that a margin provider exists for
  margin-gated txTypes, and no event when checks are off (the reported headline).
- **Out of scope** if the program treats the missing-provider state as pure owner misconfiguration (owner forgets to
  register / unregisters `Risk`) and accepts no admin-misconfiguration findings. This is the same not-wired condition
  under which F-2 was ruled out of scope — confirm before submitting.
- **Novelty:** verify against prior TipRun audits that the fail-open capability fallback is not already reported.

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Business Logic Errors / Insecure Design — safety-critical check fails open (no-op fallback)
  when a capability provider is unregistered, with no registration-time enforcement.
- **CWE (informative):** CWE-636 (Not Failing Securely / "Failing Open"); CWE-840 (Business Logic Errors).

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| Fail-open margin check; user trade creates bad debt when the provider is absent | `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H` | **7.4** | High (conditional) |

> `PR:N` because the attack action is an ordinary user trade (not privileged); `AC:H` because it requires the
> deployment to be in the missing-provider state. The CVSS band assumes that state is reachable; the headline
> severity is held at **Medium** pending confirmation that the missing-provider state is in scope (see reachability).
> Protocol/bounty severity may differ from the CVSS band.

<!-- END classification-cvss -->
