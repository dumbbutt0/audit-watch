# [Medium] Bad-debt write-off deletes debt without burning the Coin — last/only borrower leaves the stablecoin 100% unbacked (no deficit accounting)

> **Status: DRAFT for human review — NOT submitted.** Sherlock bug bounty "Monolith Stablecoin Factory"
> (id 287), `MonolithMarket/Monolith` @ `41eb720`. Human verifies + confirms against live markets before any submission.

## Summary
`Lender.writeOff()` clears an underwater borrower's debt and **socializes it onto the remaining
borrowers**, but (a) it never burns the Coin that was minted against that debt, and (b) the socialization
is **skipped whenever there is no survivor to absorb it** — because `totalDebt` is read *after* the bad
borrower's debt has already been removed. There is **no protocol-deficit / system-debt accounting** to
catch the shortfall. Consequently, when the written-off borrower is the **last (or only) debt in the
market**, 100% of the Coin it minted remains in circulation **permanently unbacked** → the stablecoin is
under-collateralized and depegs; Vault stakers and Coin holders bear the loss.

## Severity: Medium (impact High × likelihood Medium)
- **Impact: High** — breaks the core invariant that every Coin is backed by collateralized debt. In the
  last-borrower case the *entire* remaining supply becomes unbacked → insolvency / depeg.
- **Likelihood: Medium** — requires bad debt (`debt > 100 × collateralValue`), reachable by a sharp
  collateral price crash or by interest ballooning an unliquidated underwater position, **and** the
  written-off position being the last/only debt in that market (single-collateral markets naturally wind
  down to a last borrower; small/new markets may have one). The trigger itself is **permissionless**
  (`writeOff` is `external`, and it also auto-fires inside `liquidate`).
- Could be argued **High** depending on the program's view of stablecoin-insolvency severity.

## Affected code — `src/Lender.sol:379-411`
```solidity
function writeOff(address borrower, address to) external returns (bool writtenOff) {
    accrueInterest();
    uint debt = getDebtOf(borrower);
    if(debt > 0) {
        uint collateralBalance = collateralBalances[borrower];
        (uint price,, bool allowLiquidations) = getCollateralPrice();
        require(allowLiquidations, "liquidations disabled");
        uint collateralValue = price * collateralBalance / 1e18;
        if(debt > collateralValue * 100) {
            // 1. delete all of the borrower's debt
            decreaseDebt(borrower, type(uint).max);              // <-- removes `debt` from the pool totals
            // 2. redistribute excess debt among remaining borrowers
            uint256 totalDebt = totalFreeDebt + totalPaidDebt;   // <-- read AFTER removal
            if (totalDebt > 0) {                                 // <-- FALSE when borrower was the last debt
                uint256 freeDebtIncrease = debt * totalFreeDebt / totalDebt;
                uint256 paidDebtIncrease = debt - freeDebtIncrease;
                totalFreeDebt += freeDebtIncrease;
                totalPaidDebt += paidDebtIncrease;
            }
            collateralBalances[borrower] = 0;
            emit WrittenOff(borrower, to, debt, collateralBalance);
            writtenOff = true;
            // 3. send collateral to caller
            collateral.safeTransfer(to, collateralBalance);
        }
    }
}
```
Two compounding problems:
1. **No Coin is burned and no deficit is recorded.** The Coin minted on the original borrow (`adjust` →
   `coin.mint`) stays in circulation. There is no `systemDebt`/`badDebt` variable anywhere in `Lender`,
   so the shortfall is silently dropped.
2. **Socialization has no fallback.** `totalDebt` is measured *after* `decreaseDebt(borrower, max)`. If
   the borrower was the only/last debt, `totalDebt == 0`, the `if` is skipped, and `debt` is neither
   re-homed nor tracked — it just disappears, leaving its Coin unbacked.

## Proof of Concept
Foundry, against the faithfully-wired system (`Factory.deploy` → real `Coin`/`Vault`/`InterestModel`),
collateral priced by a mock Chainlink feed. File: `test/poc/WriteOffUnbackedCoin.t.sol` (2/2 pass).

`test_lastBorrower_writeOff_leaves_coin_unbacked`:
- Alice borrows **50,000 MUSD** against 100,001 collateral (50% LTV). `coin.totalSupply == 50,000e18`,
  `backing == 50,000e18`.
- Collateral crashes ~99.6% (`feed.setPrice(0.004e18)`) → `debt > 100 × collateralValue`.
- Any EOA (`keeper`) calls `lender.writeOff(alice, keeper)`.
- **Result:** `getDebtOf(alice) == 0`, `totalFreeDebt + totalPaidDebt == 0`, **`coin.totalSupply == 50,000e18`**.
  ```
  UNBACKED coin (wei): 50000000000000000000000   // entire supply unbacked
  ```
  Alice keeps the full 50,000 MUSD, debt-free.

`test_control_otherBorrower_absorbs_via_socialization` (bounding control): with a second solvent borrower
present, the socialization branch runs — bob's debt rises `50k → 100k` and `coin.totalSupply == backing`
is preserved. This confirms the defect is specifically the **no-survivor / last-borrower** path plus the
**missing deficit accounting**, not the socialization math itself.

Also surfaced independently by the invariant suite (`test/invariant/MonolithInvariant.t.sol`,
`invariant_coinBacking`): `coin.totalSupply() <= totalFreeDebt + totalPaidDebt` is violated after a
write-off.

## Recommendation
On write-off, account for the shortfall instead of dropping it. Options:
- Track an explicit `systemDebt`/deficit and cover it from `accruedLocalReserves` / surplus before it can
  be pulled, and/or socialize against `totalDebt + thisBorrowerDebt` (i.e., compute the redistribution
  basis **before** removing the borrower so a sole borrower still has a defined target), or
- If no survivor and no reserve can cover it, **mark the market insolvent / pause minting and PSM
  redemptions** so unbacked Coin cannot be redeemed 1:1 against PSM assets at the expense of last holders.
- At minimum, record the unbacked amount so off-chain/peg logic can react.

## Reviewer caveats
- The single-/last-borrower amplification is the clearest case; in multi-borrower markets the loss is
  pushed onto survivors (intended), but cascading crashes converge to the same terminal unbacked state.
- No specific live market is required — this is a code-level flaw in any deployed market that reaches the
  bad-debt condition. Confirm reachability against live Monolith markets (collateral volatility, borrower
  count) before final severity.
- Not borrower-*profit* in the clean case (collateral is lost to the write-off caller); the harm is
  protocol insolvency / depeg borne by Coin holders + Vault stakers.
