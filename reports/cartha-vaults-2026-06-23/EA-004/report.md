# EA-004 — First-depositor / inflation surface is mitigated by 1e12 virtual offset and 100k USDC minimum, but per-vault first deposit still sets the initial rate unchecked

> **DISPOSITION: REJECTED — honest negative (NOT a vulnerability).** Investigated and cleared; included for audit completeness. Do NOT submit. See Disproof / boundary below.

- **Severity (recommended):** Info
- **Category (HackenProof VRT):** Business Logic Errors
- **Triage status:** rejected
- **Confidence:** High
- **ICE:** Impact=Low · Confidence=High · Exploitability=Permissionless but unprofitable
- **Location(s):** `src/CarthaVault.sol:912-922; src/CarthaParentVault.sol:130-142`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`, `CarthaParentVault.sol`

## Description

Investigated the classic ERC-4626 first-depositor inflation vector. _convertToShares when totalShares==0||TVL==0 returns assets * 10**(18-6) = assets*1e12 (CarthaVault.sol:916-919; parent _convertToShares returns amount*1e12, CarthaParentVault.sol:133). The 1e12 decimal offset plus minimumLockAmount = 100,000e6 (each deposit must be >= 100k USDC) makes the standard 'mint 1 wei share then donate' inflation attack economically irrelevant: an attacker cannot make a 1-wei first deposit, and a 100k-USDC first deposit already mints 1e17 shares so a follow-on donation cannot round a 100k victim deposit to zero shares. Donation attack: anyone can transfer USDC directly to the vault, inflating asset.balanceOf(this) and thus TVL/share price; existing holders BENEFIT and a new depositor gets fewer shares (overpays) — but the 100k minimum + 1e12 offset bound the rounding loss to dust, and a griefer would have to donate >> the next deposit to matter, which is unprofitable (the griefer's donation is shared pro-rata). Reported Low for completeness; not a standalone exploit. NOTE this donation surface AMPLIFIES EA-001: it is another way to move TVL without minting shares, but in the deflation (not inflation) direction it is harmless.

## Impact

No profitable standalone attack under the 100k minimum + 1e12 offset; bounded rounding dust only.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Inflate share price before a victim deposit to steal via rounding.
- **Technique:** First-deposit-1-wei-then-donate (blocked by 100k min) / direct USDC donation (unprofitable, pro-rata shared).
- **Evasion:** minimumLockAmount=100k + 1e12 virtual offset neutralise the rounding edge.

## Reachability / follow-up

reachable: first deposit. no_privileged_keys: permissionless. state_before_after: shares minted at 1e12 rate. why_guards_fail: attack infeasible. scope_match: none.

## Triage reasoning

First-depositor / share-inflation (donation) attack is mitigated; honest negative (safety-net accounting class, cleared with disproof).

## Disproof / boundary

Shares are 18-dec on a 6-dec asset; the first deposit mints amount*1e12 (a 12-decimal virtual offset) and minimumLockAmount is 100_000e6. To round a victim's shares to zero an attacker would have to donate on the order of 1e22 USDC, which is economically infeasible. Donations are also shared pro-rata, so a donor cannot profit.
