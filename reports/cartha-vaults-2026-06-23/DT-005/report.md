# DT-005 — executeForceExit applies an uncapped penaltyBps

> **DISPOSITION: MERGED — duplicate.** This is the same root cause as another finding; it is kept here for traceability only and should NOT be submitted separately (see Triage reasoning for the primary).

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Improper Access Control
- **Triage status:** merged
- **Confidence:** High
- **ICE:** Impact=Medium · Confidence=High · Exploitability=Privileged (FORCE_EXITER)
- **Location(s):** `src/CarthaParentVault.sol:713-725; src/CarthaForceExit.sol:56-70`
- **Vulnerable files (bundled in `sources/`):** `CarthaParentVault.sol`, `CarthaForceExit.sol`

## Description

CarthaParentVault.executeForceExit(owner, penaltyBps) subtracts payout*penaltyBps/10000 with no upper bound (only a natural underflow revert above 100%). Currently safe because the only FORCE_EXITER is the CarthaForceExit satellite, which passes 0 or 500. Defensive: cap penaltyBps <= MAX_PENALTY_BPS so a future/extra FORCE_EXITER cannot confiscate a user's full payout.

## Impact

Bounded by FORCE_EXITER trust; hardening only.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Confiscate a user's payout via an excessive penalty.
- **Technique:** executeForceExit(user, ~9999).
- **Evasion:** Requires the FORCE_EXITER role.

## Reachability / follow-up

merged into AC-002.

## Triage reasoning

Duplicate of AC-002 (uncapped penaltyBps in executeForceExit). Merged into AC-002.
