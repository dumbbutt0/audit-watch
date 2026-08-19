# CFG-003 — Config.setBaselineSwap is permanently bricked by a double nonReentrant guard (internal _setBaselineSwap re-takes the lock and always reverts)

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** DoS with (Unexpected) revert
- **Confidence:** High
- **ICE:** Impact=setBaselineSwap always reverts; baseline-swap params must be set via generic setBool/setUint instead · Confidence=- · Exploitability=-
- **Location(s):** `contracts/config/Config.sol:257,266 (outer nonReentrant) + :275 (inner nonReentrant on internal _setBaselineSwap)`
- **Vulnerable files (bundled in `sources/`):** `Config.sol`

## Description

Both public Config.setBaselineSwap overloads (contracts/config/Config.sol:253-268) carry the `nonReentrant` modifier and then call the internal _setBaselineSwap (line 270-288), which ALSO carries `nonReentrant` (line 275). With OpenZeppelin v4 ReentrancyGuard, the outer call sets `_status = _ENTERED`; the inner `nonReentrant` then sees `_status == _ENTERED` and reverts with ReentrancyGuardReentrantCall. _setBaselineSwap is `internal` and only reachable through the two `nonReentrant` wrappers, so EVERY call to setBaselineSwap reverts — the dedicated baseline-swap config setter is non-functional. (Applying access/reentrancy modifiers to an internal function is itself a misuse; the modifier code is inlined at each internal call site, re-running the guard.) This is a 0xMarkets-custom function with no canonical GMX equivalent.

## Impact

The setBaselineSwap convenience setters always revert (liveness/DoS of that specific config function). No fund loss and no security bypass; the underlying BASELINE_SWAP_LONGS_PAY_SHORTS (bool) and BASELINE_SWAP_PER_DAY (uint) base keys are independently allowlisted (ConfigAllowedKeys.sol:209-210) and settable via the generic Config.setBool / Config.setUint, so operators retain a working path. Severity Low: broken privileged convenience function with an available alternative.

## Attack path (Intent / Technique / Evasion)

- **Intent:** n/a (not attacker-exploitable) — correctness/liveness defect: the intended config setter cannot be used.
- **Technique:** CONFIG_KEEPER calls setBaselineSwap(...); outer nonReentrant locks the guard; the body calls _setBaselineSwap whose own nonReentrant re-checks the already-entered guard and reverts. Call always fails.
- **Evasion:** The reversed-flag overload was added (custom) and the shared body factored into an internal function, but the internal function kept the `onlyConfigKeeper nonReentrant` modifiers that the public wrappers already apply, double-entering the guard.
