# AR-002 — First-deposit decimal-offset exponent (18 - assetDecimals) underflow-reverts for >18-decimal assets and collapses to 1 for 18-decimal assets

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Integer Underflow
- **Triage status:** downgraded
- **Confidence:** High
- **ICE:** Impact=Low · Confidence=High · Exploitability=Conditional (non-<18-decimal asset; ADMIN/FACTORY deploy)
- **Location(s):** `src/CarthaVault.sol:862,883,916-919`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`

## Description

shares = assets * 10 ** (decimals() - IERC20Metadata($.asset).decimals()) at CarthaVault.sol:862 and :918, with decimals() pure-returning 18. The exponent decimals() - asset.decimals() is uint8 - uint8 under Solidity 0.8 checked arithmetic. For any asset with MORE than 18 decimals the subtraction underflows and REVERTS -> first deposit (and the first-deposit branch of withdrawToParent) is permanently unavailable, DoSing the vault for that asset. For an asset with EXACTLY 18 decimals the exponent is 0 -> 10**0 = 1 -> the 1e12 virtual offset that mitigates first-depositor inflation (per INV-INFLATION-RESIST) disappears. The arithmetic is correct only for assets with FEWER than 18 decimals (the intended 6-decimal USDC gives 10**12). This is the arithmetic-axis view of TI-002. No unchecked block is used, so the underflow is a revert (fail-closed) rather than a wraparound, which limits it to DoS rather than a silent huge offset.

## Impact

With 6-decimal USDC: correct (10**12). >18-decimal asset: permanent first-deposit DoS (revert). =18-decimal asset: virtual offset becomes 1, re-enabling the first-depositor inflation edge.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Brick a vault or remove its inflation offset by relying on a decimal-offset exponent that only holds for <18-decimal assets.
- **Technique:** Configure a >=18-decimal asset; first lock either reverts (>18, underflow) or mints with offset 1 (=18, no virtual offset).
- **Evasion:** decimals() hardcoded 18; offset = 10**(18 - assetDecimals) assumes asset decimals < 18; no clamp/guard on asset decimals.

## Reachability / follow-up

reachable: only with a non-6-dec asset. no_privileged_keys: asset set by factory config. state_before_after: revert or lost offset. why_guards_fail: decimals not validated. scope_match: latent.

## Triage reasoning

First-deposit offset 10**(decimals()-assetDecimals) underflow-reverts for assets with >18 decimals (vault DoS) and collapses to 1 for exactly-18-dec assets (kills the inflation offset and the 100k floor which is hardcoded in 6-dec units). Live-safe under the intended 6-dec USDC; defensive for asset generality / factory decimal validation.
