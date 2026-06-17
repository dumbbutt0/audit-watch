# L-1 (Low) — Parent `withdraw` / `releaseFromParent` burn full shares but can underpay on rounding

- **Target:** Cartha Vaults, commit `4c51f2a…`.
- **Vulnerable file (copied in `vulnerable/`):** `src/CarthaParentVault.sol`
  (`withdraw`, `releaseFromParent`, `processQueuedParentWithdrawals`, `_prepareSharePayout`, `_withdrawFromChildren`).
- **Severity:** Low (bounded dust loss).
- **Proof type:** code analysis (no runnable PoC; dust-magnitude).

## Root cause
`withdraw` burns `_convertToSharesRoundUp(assets)` and `releaseFromParent` / `processQueuedParentWithdrawals` burn the
full `lockedShares`, but the payout is `min(shareValue/assets, balance)` after `_withdrawFromChildren`, which does a
**single proportional pass** and never loops to cover the rounding remainder:

```solidity
// _withdrawFromChildren
uint256 withdrawAmount = (amount * parentPortion) / totalIdle;  // floored, per child
...
uint256 withdrawn = ICarthaVault(vault).withdrawToParent(withdrawAmount);
remaining -= withdrawn;                                         // no second pass on the remainder
```
```solidity
// _prepareSharePayout / withdraw
uint256 balance = IERC20(asset()).balanceOf(address(this));
payout = shareValue > balance ? balance : shareValue;          // pays min(value, balance)
// ... full shares are still burned
```

The `_availableFromChildren() + 10 < needed` guard tolerates ~10 wei. Net: the caller burns shares worth `assets`
(or full `lockedShares`) but can receive slightly less when the proportional pull floors below `needed`.

## Impact
Bounded dust underpayment to the withdrawer (value retained by the vault / remaining holders). Not a theft primitive,
but a small, repeatable user loss and an accounting wart.

## Fix
Pay exactly `shareValue` / `assets` (revert if children cannot fully cover after the pull), or burn shares
proportional to the *actual* payout rather than the requested amount; add a second pass in `_withdrawFromChildren`
to cover the rounding remainder.

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Business Logic Errors (rounding/dust underpayment in parent-vault withdraw/release)
- **CWE (informative):** CWE-682 (Incorrect Calculation)

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| Withdraw/release dust underpay | `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N` | **3.7** | Low |

> Analysis-only (no runnable PoC); dust-magnitude impact.

> CVSS v3.1 base scores computed with the official formula (no temporal/environmental modifiers). For smart-contract findings the protocol/bounty severity may differ from the CVSS band; both are stated where they diverge.

<!-- END classification-cvss -->
