# LG-003 — migratePositionShares sets position.shares = balanceOf(owner), over-attributing transferred-in (non-position) shares to the position -> over-payout on release

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Business Logic Errors
- **Triage status:** downgraded
- **Confidence:** Medium
- **ICE:** Impact=Low · Confidence=Medium · Exploitability=Privileged-trigger (ADMIN migration) + conditional owner setup
- **Location(s):** `src/CarthaVault.sol:699-708,303-311,890-906`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`

## Description

migratePositionShares (699-708) backfills legacy positions where shares==0 by writing position.shares = balanceOf(owner) for the WHOLE ERC20 balance. shares are normally minted 1:1 with the position on deposit/topup, but the vault is a transferable ERC20: after a lock expires, _update (890-906) allows the owner to RECEIVE shares transferred in from other (unlocked) holders. If such an owner holds shares beyond their original position (transferred-in, or from a prior partial-release leftover) and is then migrated, position.shares is set to the inflated total. Consumers (release 304-311, forceExit 399-402, processQueuedWithdrawals 578-580) pay out min(position.shares, balanceOf) * price, so the migrated position can now claim against shares it did not deposit, over-paying that owner and diluting others. Bounded to Low/Medium: one-shot ADMIN migration intended only for pre-upgrade positions, the guard `if (position.shares > 0) continue` prevents re-running, and the attack requires the owner to have acquired extra shares pre-migration. Recommend setting shares = min(balanceOf(owner), reconstructed-from-amount) or migrating from a recorded value rather than live balanceOf.

## Impact

A migrated owner holding transferred-in shares is credited those shares to their position and can release/force-exit against them, over-paying at the expense of remaining holders. ADMIN/one-shot gated; conditional.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Inflate a position's payout by having extra shares counted into position.shares at migration.
- **Technique:** Acquire vault shares beyond the original deposit (transfer-in after lock expiry); be included in migratePositionShares while position.shares==0; position.shares := full balanceOf; release pays against the inflated shares.
- **Evasion:** Migration trusts live balanceOf as a proxy for position shares; transferability of the share token breaks that equivalence.

## Reachability / follow-up

reachable: ADMIN migratePositionShares once. no_privileged_keys: NO (ADMIN). state_before_after: position.shares set to full balance incl. transferred-in. why_guards_fail: uses balanceOf not the original mint. scope_match: migration.

## Triage reasoning

migratePositionShares sets position.shares = balanceOf(owner) when position.shares==0; since shares are a transferable ERC20, an owner who received transferred-in shares would get them over-attributed to the position -> over-payout. ADMIN one-shot, conditional, migration-only (safety-net migration class; reasoning given). Low.
