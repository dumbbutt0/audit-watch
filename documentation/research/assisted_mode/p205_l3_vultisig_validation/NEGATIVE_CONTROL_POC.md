# P205 — negative-control PoC (executed)

## V-07 — `ILOWhitelist.openToAll` access-bypass → DEMOTE (executed, 2/2 pass)
- **Harness:** `pocs/test/V07_whitelist.t.sol` (solc 0.7.6, forge 1.5.1). Imports the **real**
  `src/base/ILOWhitelist.sol` (byte-identical `realsrc/`); only external dep mocked = OZ `EnumerableSet` (faithful
  swap-and-pop AddressSet; not the analysis locus). Concrete subclass implements `onlyProjectAdmin` **exactly as the
  real concrete impls do** (`ILOPool.sol:463` / `ILOManager.sol:51` gate it on the project admin).
- **`test_bypass_requires_admin` (PASS):** an unprivileged attacker calling `setOpenToAll(true)` **reverts
  `UNAUTHORIZED`** → the bypass needs the **project-admin role** (admin prerequisite).
- **`test_bypass_flips_access_but_moves_no_funds` (PASS):** admin enabling `openToAll` flips `_isWhitelisted(attacker)`
  false→true, but the whitelist module **holds and transfers no value** — the flip is pure access permission; any
  allocation still requires `buy()` to pull the full `raiseAmount` 1:1.
- **L3 verdict: MEDIUM_OR_LOWER (DEMOTE).** Access-bypass capability + admin prerequisite + **no realized material
  impact** → fails the HIGH bar. This is the same demotion the blind over-rating (v-07 HIGH) needed.

### Honest limitation (decisive for the phase decision)
This `src/base/ILOWhitelist.openToAll` is a **by-design** admin switch and is **NOT** the awarded **H-02**. Awarded
H-02 ("whitelisting can be bypassed by anyone") is in the *other* codebase — `hardhat-vultisig/contracts/Whitelist.sol::checkWhitelist`
(an `_allowedWhitelistIndex == 0` mis-check that treats every user as initialized; permissionless), which my bounded
`src/`-only sample did not cover. So v-07 validates the **L3 demotion mechanism executably** (capability → demote) but
**not against a mapped awarded finding**. The clean awarded negative control (M-03 cap-bypass, awarded Medium / blind
HIGH) was not executable within scope — see `POSITIVE_CONTROL_POC.md` for the shared V3 compile obstacle.

Run log: `pocs/run_log.txt`.
