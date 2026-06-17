# P240 — PoolTogether V5 base blind candidate set (pre-reveal)

> Generated BLIND from the 6 in-scope source files only (`contracts/src/`). Answer key (`_sealed_answer_key/`) NOT
> opened. ICE-scored. This is the BASE-STACK set (no lens input). Advisory-lens candidates are a separate set
> (both lenses = 0; see FROZEN_HUNT.md).

Architecture: single-asset ERC4626 PrizeVault + TWAB share token + prize-claim hooks; yield is liquidated to a
liquidationPair and contributed to the PrizePool. Core invariant: `totalAssets ≥ totalDebt` (no-loss);
shares 1:1 with assets; yield buffer covers rounding.

| ID | Title | Contract:fn | I | C | E | Predicted sev |
|---|---|---|---|---|---|---|
| PT-01 | `claimYieldFeeShares` zeroes the ENTIRE `yieldFeeBalance` (`-= _yieldFeeBalance`) but mints only `_shares` → a partial claim forfeits the remaining accrued fee | PrizeVault:claimYieldFeeShares (617) | Medium | High | Privileged (yieldFeeRecipient) | **Medium** |
| PT-02 | `_withdraw` uses raw `_asset.transfer(receiver, assets)` ignoring the return value (not SafeERC20) → a non-standard ERC20 returning false burns shares without sending assets | PrizeVault:_withdraw (939) | Medium | Medium | Conditional (non-standard asset) | **Low/Med** |
| PT-03 | `PrizeVaultFactory.deployVault` raw `transferFrom` (return ignored) for the yield-buffer donation → buffer may be unfunded for non-standard assets | PrizeVaultFactory:deployVault (118) | Low | Medium | Conditional | **Low** |
| PT-04 | Prize-claim hooks (`beforeClaimPrize`/`afterClaimPrize`, winner-set, 150k gas) — a reverting/malicious hook can grief the claimer (claim reverts, claimer wastes gas) | Claimable:claimPrize (76) | Medium | Medium | Permissionless (winner sets own hook) | **Med/Low** |
| PT-05 | `transferTokensOut` yield-fee math `_yieldFee = amountOut*P/(P-fee) - amountOut` + share-vs-asset liquidation rounding — possible rounding edge | PrizeVault:transferTokensOut (659) | Low | Speculative | Privileged (LP) | **Low** |

## Flagship reasoning — PT-01 (the strongest base finding)
`claimYieldFeeShares(_shares)`:
```
uint256 _yieldFeeBalance = yieldFeeBalance;
if (_shares > _yieldFeeBalance) revert ...;
yieldFeeBalance -= _yieldFeeBalance;   // BUG: subtracts the FULL balance, not _shares
_mint(msg.sender, _shares);
```
A yield-fee recipient who claims `_shares < yieldFeeBalance` mints only `_shares` but the whole `yieldFeeBalance` is
zeroed — the unminted remainder is forfeited (it drops out of `totalDebt`, returning to the available-yield pool).
Should be `yieldFeeBalance -= _shares`. Privileged (onlyYieldFeeRecipient) and self-affecting, so likely Medium.

## Lens applicability (blind, pre-reveal)
- **Safe-management lens:** no Gnosis-Safe guard in scope → expected 0. (Confirmed 0.)
- **Hostile-token settlement lens:** single immutable `_asset`, no order/array-selected token; transfers go to the
  caller (withdraw/redeem) or to the trusted liquidationPair receiver of the FIXED asset → outside the lens domain
  (needs an attacker/order-selected token) → expected 0. (Confirmed 0.) PT-02's raw-transfer is on the immutable
  asset, which the lens deliberately suppresses.
