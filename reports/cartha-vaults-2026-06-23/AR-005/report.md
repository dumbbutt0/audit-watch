# AR-005 — uint64(block.timestamp) casts on lock timestamps/cooldown/epoch are safe until year 2554; penalty subtraction is underflow-guarded by MAX_PENALTY_BPS but executeForceExit penaltyBps is uncapped

> **DISPOSITION: REJECTED — honest negative (NOT a vulnerability).** Investigated and cleared; included for audit completeness. Do NOT submit. See Disproof / boundary below.

- **Severity (recommended):** Info
- **Category (HackenProof VRT):** Timestamp Dependence
- **Triage status:** rejected
- **Confidence:** High
- **ICE:** Impact=Low · Confidence=High · Exploitability=Privileged (executeForceExit penalty) / not reachable (timestamp & cast overflows)
- **Location(s):** `src/CarthaVault.sol:228,289,455,814-817; src/CarthaParentVault.sol:613-617,721; src/diamond/LibDiamond.sol:92-103; src/libraries/PoolDeployLib.sol:106-108`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`, `CarthaParentVault.sol`, `LibDiamond.sol`, `PoolDeployLib.sol`

## Description

Reviewed all timestamp casts and penalty arithmetic. (1) uint64(block.timestamp) is used for position.start, cooldownEnds, lastEpoch (CarthaVault.sol:228,235-237,271,405,466,814-817; CarthaParentVault.sol:569,575,598) — uint64 holds timestamps until ~year 2554, no truncation risk this century. lockDays math: position.start + uint256(position.lockDays) * 1 days (CarthaVault.sol:289,549,574,898,980,1002; CarthaParentVault.sol:631,670,693,794,804) widens to uint256 before the multiply (lockDays cast to uint256), and lockDays <= MAX_LOCK_DAYS_LIMIT (1825) so 1825*86400 ~ 1.6e8 << uint256 max — no overflow. cooldownEnds = currentTime + uint64(cooldownDuration) where cooldownDuration <= 30 days (setCooldownDuration guard) so the uint64 cast and addition cannot overflow. extendLock: newLockDays = position.lockDays + extensionDays (uint64+uint64) is bounded by the newLockDays <= maxLockDays (<=1825) check AFTER the add, and the add itself is checked (0.8) so an overflowing extensionDays reverts (fail-closed) before the bound check. (2) Penalty subtraction payout - (payout * performancePenalty)/10000 (CarthaVault.sol:455) cannot underflow because performancePenalty <= MAX_PENALTY_BPS (2000) via setPerformancePenalty, so the deduction is <= 20% < payout. BUT CarthaParentVault.executeForceExit: payout -= (payout * penaltyBps)/BASIS_POINTS (CarthaParentVault.sol:721) takes penaltyBps from the FORCE_EXITER with NO upper bound — only a natural underflow revert if penaltyBps > 10000 (the product exceeds payout). That is DT-005 (Low, FORCE_EXITER-trusted). (3) uint96 selectorPosition in LibDiamond.addFunctions (LibDiamond.sol:92,103,115,170) cannot realistically overflow (would require 2^96 selectors per facet). No signed/unsigned mix issues; gmPrice is int256 and guarded gmPrice <= 0 -> return 0 (PoolDeployLib.sol:106) before the uint256 cast, so a negative price never becomes a huge uint.

## Impact

No exploitable overflow/underflow/cast truncation in timestamp or penalty math under the configured bounds. The only residual is the uncapped executeForceExit penaltyBps (DT-005, FORCE_EXITER-trusted, hardening).

## Attack path (Intent / Technique / Evasion)

- **Intent:** Overflow/underflow a timestamp, lock, or penalty computation to skip a lock or zero a payout.
- **Technique:** Checked: timestamp casts (uint64 safe to 2554), lockDays*1days (bounded 1825), penalty subtraction (bounded by MAX_PENALTY_BPS in vault; uncapped in parent executeForceExit but FORCE_EXITER-gated and underflow-reverting), uint96 selectorPosition (infeasible).
- **Evasion:** n/a — bounds enforced by setters and checked arithmetic; negative gmPrice short-circuited before uint cast.

## Reachability / follow-up

reachable: all lock paths. no_privileged_keys: n/a. state_before_after: timestamps stored. why_guards_fail: it does not. scope_match: none.

## Triage reasoning

uint64(block.timestamp) casts on lock/cooldown/epoch are safe; honest negative (safety-net time-gate class, cleared with disproof).

## Disproof / boundary

uint64 holds up to ~5.8e11 (year 2554); block.timestamp will not overflow uint64 for ~530 years. lockDays is widened to uint256 in the lock-expiry math (start + uint256(lockDays)*1 days) and bounded <= 1825, so the addition cannot overflow. The penalty subtraction is underflow-safe via MAX_PENALTY_BPS, and negative gmPrice is short-circuited before the uint cast.
