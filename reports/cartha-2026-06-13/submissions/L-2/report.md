# L-2 (Low) — Child vault shares are transferable post-lock but only redeemable via a Position

- **Target:** Cartha Vaults, commit `4c51f2a…`.
- **Vulnerable file (copied in `vulnerable/`):** `src/CarthaVault.sol` (`_update`, `release`, `forceExit`,
  `processQueuedWithdrawals` — no permissionless `redeem`-by-shares).
- **Severity:** Low (footgun / potential user fund loss; not a protocol-theft primitive).
- **Proof type:** code analysis.

## Root cause
`CarthaVault` mints ERC20 shares to depositors and exposes redemption **only through a Position** (`release`,
`forceExit`, `forceExitUnderperformer`, `processQueuedWithdrawals`), each capped at the owner's stored position.
There is no position-independent `redeem(shares)`. Meanwhile, shares are ERC20-transferable once the lock expires —
`_update` only blocks transfers while a position is locked:

```solidity
function _update(address from, address to, uint256 value) internal override {
    if (from != address(0) && to != address(0)) {
        Position storage position = $.positions[lockIdOf(from, $.poolId)];
        if (position.exists) {
            bool locked = block.timestamp < position.start + uint256(position.lockDays) * 1 days;
            if (locked) revert PositionLocked();
        }
    }
    super._update(from, to, value);
}
```

So shares transferred to an address **without a Position** (e.g. sold/sent post-lock, or a holder whose position was
fully released) are **orphaned: non-redeemable**, yet they still count in `totalSupply`, diluting `_convertToAssets`
for everyone else.

## Impact
A user who acquires child shares by transfer cannot redeem them — potential loss of funds for anyone treating the
share token as a fungible/redeemable 4626 share. The orphaned supply also skews share-price math for remaining
holders.

## Fix
Make child shares non-transferable (soulbound to the position), or add a position-independent `redeem(shares)`, or
clearly document that child shares are redeemable only by the original position owner.

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Business Logic Errors (child shares are ERC-20-transferable after lock but redemption is position-bound → transferred shares are not redeemable by the recipient)
- **CWE (informative):** CWE-840 (Business Logic Errors)

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| Transferable-but-bound shares | `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N` | **3.7** | Low |

> Low — a holder can orphan value by transferring locked shares; no theft from the protocol.

> CVSS v3.1 base scores computed with the official formula (no temporal/environmental modifiers). For smart-contract findings the protocol/bounty severity may differ from the CVSS band; both are stated where they diverge.

<!-- END classification-cvss -->
