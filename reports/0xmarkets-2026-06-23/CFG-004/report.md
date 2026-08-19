# CFG-004 — LIMITED_CONFIG_KEEPER path is dead code: onlyKeeper admits the role but _validateKey's LIMITED branch is commented out, so a LIMITED-only keeper is fully locked out (fail-closed)

> **DISPOSITION: INFO — informational / hardening note.** Not a security vulnerability on its own.

- **Severity (recommended):** Info
- **Category (HackenProof VRT):** Business Logic Errors
- **Confidence:** High
- **ICE:** Impact=LIMITED_CONFIG_KEEPER role inert (fail-closed); no escalation · Confidence=- · Exploitability=-
- **Location(s):** `contracts/config/Config.sol:46-55 (onlyKeeper admits LIMITED), :476-494 (_validateKey LIMITED branch commented out), :43 (_initAllowedLimitedBaseKeys disabled); cf. gmx-synthetics Config.sol:634-640 (canonical LIMITED branch present)`
- **Vulnerable files (bundled in `sources/`):** `Config.sol`

## Description

Config.onlyKeeper (contracts/config/Config.sol:46-55) still admits a caller holding EITHER LIMITED_CONFIG_KEEPER or CONFIG_KEEPER, identical to canonical GMX. However, Config._validateKey (lines 476-494) has the entire LIMITED_CONFIG_KEEPER branch commented out (lines 485-491): it only special-cases CONFIG_KEEPER (checking allowedBaseKeys), and otherwise falls through to `revert Errors.InvalidBaseKey(baseKey)`. The companion allowlist initializer was also disabled — Config's constructor only calls ConfigAllowedKeys.initAllowedBaseKeys and leaves `_initAllowedLimitedBaseKeys()` commented out (line 43), and allowedLimitedBaseKeys is never populated. Net effect: an account holding ONLY LIMITED_CONFIG_KEEPER (and not CONFIG_KEEPER) passes onlyKeeper but then hits _validateKey, where it matches neither branch and reverts on every base key. The LIMITED keeper role is therefore inert. This is FAIL-CLOSED (more restrictive than canonical, where a LIMITED keeper can write a small curated whitelist of risk params), so it is NOT a privilege escalation — it is a design regression / dead code that silently disables the intended fast-tuning role. Worth noting because the role still exists, can be granted, and would mislead an operator into thinking a LIMITED keeper can tune params when in fact every such call reverts.

## Impact

Operational only: the LIMITED_CONFIG_KEEPER role is non-functional (every setUint/setBool/etc. by a LIMITED-only keeper reverts InvalidBaseKey). No security loss — it is strictly more restrictive than canonical. No privilege escalation, no draining path. Informational/defense-in-depth note.

## Attack path (Intent / Technique / Evasion)

- **Intent:** n/a — not exploitable; documented for completeness (fail-closed regression).
- **Technique:** LIMITED_CONFIG_KEEPER-only account calls Config.setUint(...); passes onlyKeeper; _validateKey finds no CONFIG_KEEPER role and no LIMITED branch -> reverts InvalidBaseKey. Role is inert.
- **Evasion:** Canonical gates LIMITED keepers to allowedLimitedBaseKeys; 0xMarkets commented out both the LIMITED _validateKey branch and the allowlist initializer, leaving onlyKeeper's LIMITED admittance with no matching validation path.
