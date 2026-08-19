# DT-004 — GM-pricing inputs (oracle/reader/marketToken/dataStore) are ADMIN-settable with no timelock or immutability

- **Severity (recommended):** Medium
- **Category (HackenProof VRT):** Violation of Secure Design Principles
- **Triage status:** submit
- **Confidence:** High
- **ICE:** Impact=High (share-price control) · Confidence=High · Exploitability=Privileged (ADMIN)
- **Location(s):** `src/CarthaVault.sol:713-765; src/libraries/PoolDeployLib.sol:97-127`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`, `PoolDeployLib.sol`

## Description

setReader/setOracle/setDataStore/setMarketToken/setPoolToken validate only against the zero address. These feed gmValueInUsdc() -> share price. A compromised or malicious ADMIN can repoint pricing to attacker-controlled contracts and corrupt share price (mint cheap / redeem rich). Centralization/trust finding; recommend immutability post-setup or a timelock + sanity bounds.

## Impact

Full control of GM valuation and therefore share price via the pricing seam.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Corrupt share price by controlling the pricing oracle.
- **Technique:** setOracle/setReader/setMarketToken to malicious addresses.
- **Evasion:** Legitimate ADMIN role.

## Reachability / follow-up

reachable: ADMIN setOracle/setReader/setMarketToken. no_privileged_keys: NO (ADMIN). state_before_after: share price repriced via attacker-chosen oracle. why_guards_fail: only zero-addr validation. scope_match: centralization / pricing trust root.

## Triage reasoning

All GM-pricing inputs (oracle/reader/dataStore/marketToken/poolToken) are ADMIN-settable with only zero-address checks — no timelock, immutability, or sanity bound — and feed gmValueInUsdc -> share price. Reported as a centralization/trust finding (safety-net oracle code; not silently cleared — flagged for governance/timelock). Recommend immutability post-setup or a timelock.
