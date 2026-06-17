# P158 — Defense Map (PrizeVault deposit/withdraw rate mismatch)

| Defense | Location | Classification | Reason |
|---|---|---|---|
| `LossyDeposit` revert in `_depositAndMint` | `PrizeVault.sol:874` (`if (totalAssets() < totalDebt()) revert LossyDeposit(...)`) | **blocks_candidate** | A deposit/mint cannot complete if it would leave the vault lossy → the 1:1 `previewDeposit`/`previewMint` can never mint at the "wrong" rate in a lossy state. |
| Debt-aware `previewWithdraw` | `:454-466` (`mulDiv(totalDebt, totalAssets, Up)` when lossy) | **blocks_candidate** | Withdrawals in a lossy state burn *more* shares per asset (rounding Up, in the vault's favor) → no 1:1 over-withdrawal. |
| Debt-aware `previewRedeem`/`convertToAssets` | `:470-372` | **blocks_candidate** | Redemptions return a proportional haircut in a lossy state → shares are not over-valued. |
| Yield buffer (`yieldBuffer`, `totalDebt = totalSupply + buffer` allocation) | `:790, :573` | partially_covers | Absorbs small rounding/first-depositor effects so the vault doesn't trivially flip lossy. |
| `_twabSupplyLimit` (uint96 TWAB cap) | `:798` | irrelevant (to this hypothesis) | Caps supply; not related to the rate-mismatch axis. |

## Does the defense run before or after the loss?
The `LossyDeposit` guard runs **at the end of every deposit/mint**, reverting the whole transaction before any
mis-rate can settle. Withdraw/redeem use debt-aware previews **at quote time**. So the relevant defenses run
**before any loss can be realized** → the candidate mechanism is neutralized.

## Net
Two independent, explicit guards (`LossyDeposit` + debt-aware withdraw/redeem) each block the hypothesised
rate mismatch. The candidate is a **static false positive** on this axis.
