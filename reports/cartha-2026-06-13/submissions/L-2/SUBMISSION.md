<!--
PLATFORM-PASTE-READY version of the Cartha L-2 report. Plain prose + standard code fences only — no blockquote
header, no viewer "Copy"/language-label artifacts. Paste each labelled section into the matching field. This is
an ANALYSIS-ONLY finding (code path, no runnable PoC) — Validation steps describe the code; no fabricated test
output. Facts are identical to report.md. Copy from the RAW file, not a rendered preview.

NOTE: Cartha was supplied as a dropped zip (commit 4c51f2a), not a known bounty URL — confirm the correct
Target/program before submitting.
-->

# Field: Target
Cartha Vaults (Bittensor SN35 liquidity vaults over 0xMarkets GM pools) — commit 4c51f2a
(repo supplied as an archive; confirm the official submission target/URL before submitting)

# Field: Category
Business Logic Errors

# Field: Severity
Low

# Field: Title
Child vault shares are transferable after lock but only redeemable via a Position, leaving orphaned non-redeemable shares

# Field: Vulnerability details

`CarthaVault` mints ERC20 shares to depositors but exposes redemption only through a Position (`release`,
`forceExit`, `forceExitUnderperformer`, `processQueuedWithdrawals`), each capped at the owner's stored
position; there is no position-independent `redeem(shares)`. Meanwhile shares are ERC20-transferable once the
lock expires (`_update` only blocks transfers while a position is locked). Shares transferred to an address
without a Position are therefore orphaned: they cannot be redeemed by the recipient, yet still count in
`totalSupply` and dilute share-price math for everyone else.

This is Low because it is a footgun / potential user fund-loss (for anyone treating the share token as a
fungible, redeemable 4626 share), not a protocol-theft primitive — no attacker gains the lost value; it is
stranded.

## Root cause

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

`_update` blocks transfers only while a position is locked; after the lock (or for a holder whose position was
fully released) shares move freely, but redemption remains bound to a Position the recipient does not have.

## Impact

A user who acquires child shares by transfer cannot redeem them — potential loss of funds for anyone treating
the share token as a fungible/redeemable 4626 share. The orphaned supply also skews `_convertToAssets`
share-price math for remaining holders.

## Suggested fix

Make child shares non-transferable (soulbound to the position), or add a position-independent `redeem(shares)`,
or clearly document that child shares are redeemable only by the original position owner.

# Field: Validation steps

Proof type: code analysis (no runnable PoC). The behaviour is established directly from the source:

1. `CarthaVault._update` (shown above) reverts transfers only while a position is `locked`; once unlocked, ERC20
   `transfer`/`transferFrom` succeed normally to any address.
2. The only redemption entrypoints — `release`, `forceExit`, `forceExitUnderperformer`,
   `processQueuedWithdrawals` — all resolve the caller/owner's `Position` and cap redemption at that stored
   position; none accept a bare share amount.
3. Therefore an address that holds shares but has no `Position` (a post-lock transferee, or an owner whose
   position was fully released) has no path to redeem, while its balance still contributes to `totalSupply`.

# Field: Attachments
- vulnerable/CarthaVault.sol   (affected source: _update + redemption entrypoints)
