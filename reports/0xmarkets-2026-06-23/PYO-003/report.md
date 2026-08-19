# PYO-003 — PythHermesFeedProvider expo->multiplier conversion uses fully keeper-supplied expo with no bounds; out-of-range expo causes revert/DoS and price-min underflow (price-conf) is unguarded

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Business Logic Errors
- **Confidence:** High
- **ICE:** Impact=Price-construction revert (token pricing DoS) or rescaled price · Confidence=- · Exploitability=-
- **Location(s):** `/home/dummy/clones/0xMarkets_contract-main/contracts/oracle/PythHermesFeedProvider.sol:29-37`
- **Vulnerable files (bundled in `sources/`):** `PythHermesFeedProvider.sol`

## Description

In PythHermesFeedProvider.getOraclePrice (PythHermesFeedProvider.sol:29-37) the scaling multiplier is computed from the caller-supplied int32 expo: if expo>=0, multiplier = 10**(30 + uint32(expo)); else multiplier = 10**(30 - uint32(-expo)). For genuine Pyth prices expo is small-negative (e.g. -8) so this is fine, but expo is untrusted keeper input with no validation: (a) expo >= 49 makes 10**(30+expo) exceed uint256 max -> revert; (b) expo < -30 makes (30 - uint32(-expo)) underflow in unsigned exponent arithmetic -> reverts or yields a nonsensically tiny multiplier; (c) for very negative expo down to -30 the multiplier becomes 1, silently truncating precision. Additionally minPrice = (price - conf) * multiplier (line 36) is computed without checking conf <= price; if conf > price the subtraction underflows and reverts (Solidity 0.8 checked math) -- a softer failure than the Lazer provider, which has an explicit InvalidPythLazerScaledConfidence guard. None of these are attacker-reachable (CONTROLLER-gated and, for Lazer, signature-bound), but they make the Hermes path brittle: a malformed report bricks pricing for the affected token rather than failing gracefully, and the missing expo bounds mean the provider trusts an unverified exponent that directly scales the on-chain price by 10**expo.

## Impact

Malformed or mis-supplied expo/conf in the Hermes report reverts price construction (token-level pricing DoS) or, within the unbounded expo range, scales the stored price by an unverified power of ten. Reachable only by the CONTROLLER keeper; no unprivileged path. Robustness/correctness defect.

## Attack path (Intent / Technique / Evasion)

- **Intent:** n/a (robustness; keeper-only).
- **Technique:** Keeper passes a report with out-of-range expo or conf>price; multiplier overflow/underflow or (price-conf) underflow reverts; or expo silently rescales the price.
- **Evasion:** No validation of expo range or conf<=price in the Hermes provider, unlike the Lazer provider's explicit scaled-confidence guard.
