# I-2 (Low) — `triggerFactor` unset-default of 0 means "inject on any drawdown" (inverted-safe default)

- **Target:** 0xMarkets (GMX Synthetics fork), commit `e94daee…`.
- **Vulnerable file (copied in `vulnerable/`):** `contracts/insurance/InsuranceFundUtils.sol` (`attemptInjectPool`,
  ~lines 196-205).
- **Severity:** Low (config footgun).
- **Proof type:** code analysis (no runnable PoC — requires the full GMX build; logic is plain from source).

## Root cause
```solidity
uint256 triggerFactor = dataStore.getUint(Keys.insuranceFundDrawdownTriggerFactorKey(market.marketToken));
if (triggerFactor == type(uint256).max) { return 0; }   // "off" sentinel
...
if (_drawdownBefore <= triggerFactor) { return 0; }     // else: inject when drawdown > triggerFactor
```
The "off" sentinel is `type(uint256).max`, but the **unset DataStore default is 0** — which means *inject on any
drawdown > 0*. A market that has accrued insurance reserve (from liquidation-fee slices) but whose
`insuranceFundDrawdownTriggerFactor` was never explicitly set to `type(uint256).max` will drain its reserve into the
pool on the slightest realized drawdown. The safe default is inverted; the code comment flags it as a deploy-script
responsibility.

## Impact
A misconfigured / not-fully-onboarded market silently auto-drains its insurance reserve. Bounded (reserve only), but
defeats the fund's purpose for that market.

## Fix
Treat the unset value (0) as **disabled**, or require explicit enablement (store an `enabled` flag), so the
unconfigured state is fail-safe rather than fail-open.

## Note
A standalone PoC requires the full GMX build (the insurance lib pulls `MarketUtils`/`DataStore`/`@openzeppelin-v4`);
reported as a code-verified config finding.

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Unsecure Design → Violation of Secure Design Principles (`triggerFactor` unset-default 0 means inject-on-any-drawdown; the disable sentinel is `uint256` max, an unsafe default)
- **CWE (informative):** CWE-1188 (Insecure Default Initialization of Resource); CWE-657 (Violation of Secure Design Principles)

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| Unsafe default trigger config | `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:N` | **2.2** | Low |

> Config/design finding (analysis-only). PR:H — depends on deployment config.

> CVSS v3.1 base scores computed with the official formula (no temporal/environmental modifiers). For smart-contract findings the protocol/bounty severity may differ from the CVSS band; both are stated where they diverge.

<!-- END classification-cvss -->
