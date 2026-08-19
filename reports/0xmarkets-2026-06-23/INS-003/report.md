# INS-003 — Unset insuranceFundDrawdownTriggerFactor defaults to 0 ('inject on any drawdown'); a market onboarded without explicitly setting the type(uint256).max off-sentinel will inject on the slightest drawdown

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Business Logic Errors
- **Confidence:** High
- **ICE:** Impact=Medium · Confidence=High · Exploitability=Conditional
- **Location(s):** `contracts/insurance/InsuranceFundUtils.sol:196-213`
- **Vulnerable files (bundled in `sources/`):** `InsuranceFundUtils.sol`

## Description

attemptInjectPool (InsuranceFundUtils.sol:196-205) treats type(uint256).max as the 'off' sentinel, but the DataStore default for an unset uint key is 0. With triggerFactor==0 the guard `_drawdownBefore <= triggerFactor` (line 211) is false for any non-zero drawdown, so injection proceeds on the smallest drawdown. The code comment explicitly acknowledges this ('the unset-by-default state is the wrong direction ... Operators must explicitly set type(uint256).max') and pushes the safety burden entirely onto the deploy script / Config keeper. There is no on-chain guard that refuses injection for a market that has a snapshot (epochPoolValue!=0) but no explicitly-configured trigger. If snapshotEpoch is ever run for a market before INSURANCE_FUND_DRAWDOWN_TRIGGER_FACTOR is set to max, the fund auto-drains into that pool on the next decrease/liquidation/ADL at any drawdown, amplifying INS-001.

## Impact

A configuration/initialization-order mistake (no explicit trigger set) silently flips the fund into 'inject on any drawdown' mode for that market, draining reserves with effectively no threshold. Fail-open default direction for a safety-net parameter.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Drain the insurance reserve into a pool by exploiting the wrong-direction default of an un-set, safety-critical threshold.
- **Technique:** For any market where INSURANCE_FUND_DRAWDOWN_TRIGGER_FACTOR was never explicitly written (value 0) but a snapshot exists, any drawdown>0 causes attemptInjectPool to inject up to the full reserve on the next keeper-executed close.
- **Evasion:** The developer intends type(uint256).max to mean 'disabled' and 0 to be impossible in practice, but the DataStore zero-default makes 'disabled' the value an operator must remember to write, and nothing on-chain enforces it; the protection is documentation, not code.

## Reachability / follow-up

Conditional
