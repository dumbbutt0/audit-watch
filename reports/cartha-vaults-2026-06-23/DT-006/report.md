# DT-006 — No reentrancy guards; safety relies on non-callback asset + trusted externals

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Reentrancy
- **Triage status:** downgraded
- **Confidence:** Medium
- **ICE:** Impact=Medium (if asset assumption breaks) · Confidence=Medium · Exploitability=Conditional
- **Location(s):** `src/CarthaVault.sol:280-337,847-873; src/CarthaParentVault.sol:625-704`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`, `CarthaParentVault.sol`

## Description

Neither vault uses ReentrancyGuard. release/withdrawToParent/releaseFromParent/processQueuedWithdrawals do external token transfers and cross-contract calls. Safe today because the asset is non-callback USDC and pool/child calls go to trusted contracts, but a callback-capable asset, or a malicious child added to a parent, would open reentrancy. Defensive: add nonReentrant to state-mutating external entrypoints and follow strict CEI.

## Impact

Latent; no exploit under the current USDC + trusted-children assumption.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Re-enter during a payout to double-spend.
- **Technique:** Callback token / malicious child re-entering release.
- **Evasion:** n/a under current config.

## Reachability / follow-up

reachable: only if asset has transfer hooks or a malicious child is added. no_privileged_keys: child-add is ADMIN/FACTORY. state_before_after: potential double-payout on re-entry. why_guards_fail: no guard; relies on token/child trust. scope_match: defensive.

## Triage reasoning

No ReentrancyGuard on any state-mutating external entrypoint. Safe today because the asset is non-callback USDC and pool/child calls go to trusted contracts (safety-net reentrancy class; reasoning given, not silently cleared). Defensive: add nonReentrant + strict CEI so a future callback-capable asset or a malicious child cannot re-enter release/withdraw.
