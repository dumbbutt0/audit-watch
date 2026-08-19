# UP-003 — Parent retains a DEPRECATED `positions` mapping mid-struct to preserve storage layout — correct, but it is a layout landmine for future upgrades

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Other
- **Triage status:** submit
- **Confidence:** High
- **ICE:** Impact=All lock positions mis-read -> wrong payouts / lock bypass / bricked releases. · Confidence=- · Exploitability=-
- **Location(s):** `/home/dummy/clones/cartha-vaults-main/src/CarthaParentVault.sol:39`
- **Vulnerable files (bundled in `sources/`):** `CarthaParentVault.sol`

## Description

ParentVaultStorage keeps `mapping(address => Position) positions; // @dev DEPRECATED` (line 39) sandwiched between `vaultIndex` and `rebalanceConfig`. Inside an erc7201 namespaced struct, fields are laid out sequentially from the struct base, so a mapping occupies one reserved slot whose VALUE slots are computed elsewhere; removing or reordering this field in a future implementation would shift every subsequent field (rebalanceConfig, lastRebalanceTime, lockPositions, lockNonces, parentPendingWithdrawal, maxLockDays, cooldownDuration, minimumLockAmount) down by one slot, silently corrupting all lock accounting (lockPositions would read garbage). Retaining it as DEPRECATED is the CORRECT defensive choice and is currently safe (the deprecated mapping is never read/written, so it just holds dead state). The finding is purely a future-upgrade hazard: there is no storage-gap reservation in any of the three erc7201 structs (CarthaVaultStorage, ParentVaultStorage, CarthaVaultFactoryStorage). erc7201 namespacing means each contract's struct is collision-isolated, so new fields APPENDED at the end of a struct are safe without a gap; but any developer who removes the DEPRECATED field, reorders fields, or changes a field's type/width will shift the tail and corrupt live positions. There is no automated check enforcing append-only here. Recommend: never remove/reorder; only append; add an explicit comment-locked layout or a CI storage-layout diff. No current exploit.

## Impact

If a future upgrade removes/reorders the DEPRECATED positions mapping (or any mid-struct field), all subsequent fields — including lockPositions, lockNonces, and parentPendingWithdrawal — read from the wrong slots, corrupting every locker's accounting (wrong shares/amount/cooldown -> wrong payouts, bypassed locks, or bricked releases).

## Attack path (Intent / Technique / Evasion)

- **Intent:** A future (well-meaning) upgrade deletes the DEPRECATED positions mapping to tidy the struct, shifting all later fields and corrupting live lock accounting.
- **Technique:** New impl removes line 39; lockPositions (was slot base+8) now resolves to base+7, reading the old rebalanceConfig/lastRebalanceTime bytes as a LockPosition; lockNonces / parentPendingWithdrawal likewise shift; releaseFromParent/executeForceExit then operate on garbage shares/amounts.
- **Evasion:** The current code already does the right thing (keeps the deprecated field), but nothing structural (no __gap, no layout lock, no CI diff) prevents a future maintainer from breaking it; the safety relies entirely on the inline DEPRECATED comment being heeded.

## Reachability / follow-up

reachable: future upgrade. no_privileged_keys: NO (ADMIN upgrade). state_before_after: a layout change corrupts lock storage. why_guards_fail: no __gap / layout lock. scope_match: upgrade safety.

## Triage reasoning

CarthaParentVault keeps a mid-struct `mapping positions; // DEPRECATED` with no __gap or layout lock in any of the erc7201 structs. Keeping it is currently correct, but removing/reordering it in a future impl would shift lockPositions/lockNonces/parentPendingWithdrawal and corrupt all lock accounting. Upgrade-checklist hardening (Low).
