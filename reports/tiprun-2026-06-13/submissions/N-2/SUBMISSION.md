<!--
PLATFORM-PASTE-READY version of the N-2 report. Plain prose + standard code fences only. Paste each labelled
section into the matching platform field. Facts are identical to the PoC (validated, all tests passing). Copy from
the RAW file, not a rendered preview.
-->

# Field: Target
https://github.com/hackenproof-public/tiprun-contracts

# Field: Category
Business Logic Errors

# Field: Severity
Medium (High only if the missing-provider state is in-scope reachable — see scope caveat)

# Field: Title
Perp margin checks fail open when CAP_MARGIN_CHECK is absent, allowing insolvent trades if the Risk provider is not registered

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

…and no plugin declares CAP_MARGIN_CHECK as required. In particular the TYPE_TRADE handler OrderbookPlugin does not
override requiredCapabilities() (inherits BasePlugin's empty default), so the full trading surface can be registered
with no margin provider — the safety net is opt-out by omission and the system fails OPEN, not closed.

## Impact

On a perp deployment with no CAP_MARGIN_CHECK provider, a NORMAL user-signed trade that the real Risk check would
reject is accepted, opening a position far below maintenance margin -> bad debt the protocol absorbs. Proven via the
ordinary user path (a relayed TYPE_TRADE, not an owner call): with the provider wired the trade reverts "PM: risk
inc"; with it absent the identical trade is accepted, leaving maintenance risk 9.2e22 vs value 4.3e9 (risk >>
value*FXP). The PoC proves position OPENING (bad-debt creation); it does not claim a withdrawal/exfiltration path.

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

What it proves (three tests, all through the real user path):

1. test_PoC_tradePluginDoesNotRequireMarginCapability: reads the live registry — the TYPE_TRADE plugin
   (OrderbookPlugin) declares ZERO required capabilities, so registerPlugin accepts the trading surface with no
   CAP_MARGIN_CHECK provider (missing-provider state reachable by deployment omission).
2. test_sameUserTradeRevertsWhenRiskProviderRegistered (negative control): with the real Risk provider wired, a
   normal signed trade routed txBatcher -> MultiTransactionProcessor -> OrderbookPlugin -> PositionManager.updatePosition
   is REJECTED with "PM: risk inc". The margin check, not the harness, is the only thing flipping the outcome.
3. test_PoC_userTradeAcceptedWhenPerpMarginProviderMissing: the provider-absent state is set up via an owner call
   (setup only, NOT the attack action); the identical normal user-signed trade is then ACCEPTED, leaving the account
   far below maintenance margin (risk > value*FXP).

Captured output (real run, all passing):

```
[PASS] test_PoC_tradePluginDoesNotRequireMarginCapability()
[PASS] test_PoC_userTradeAcceptedWhenPerpMarginProviderMissing()
Logs:
  B synthetic short: 5000
  B account value (FXP): 4294967296
  B maintenance risk (FXP^2): 92233720368547758080000
[PASS] test_sameUserTradeRevertsWhenRiskProviderRegistered()

Suite result: ok. 3 passed; 0 failed; 0 skipped
```

# Field: Scope caveat (read before submitting)

The attack action is a normal user trade and the negative control + capability tests remove the "harness manufactured
it" objection. What remains uncertain is whether the missing-provider state is in scope:
- HIGH if a real in-scope perp deployment can reach CAP_MARGIN_CHECK == address(0) while trading is live (e.g. a
  deploy/upgrade window registering OrderbookPlugin before/without RiskPlugin, or a perp profile that omits it).
- MEDIUM as a fail-open design defect (no on-chain assertion that a margin provider exists for margin-gated txTypes).
- OUT OF SCOPE if the program treats the missing-provider state as pure owner misconfiguration — the same not-wired
  condition under which the related risk-segment finding (F-2) was ruled out of scope. Confirm before submitting.

# Field: Attachments
- PoC_CapabilityRegistryNoop.t.sol
- poc_output.log   (captured passing run)
