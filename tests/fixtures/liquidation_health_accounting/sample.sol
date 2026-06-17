// SPDX-License-Identifier: MIT
// Fixture for the liquidation_health_accounting research prototype. One scenario per function.
pragma solidity ^0.8.0;

contract Seed {
    // 1+2. H-03 cap + H-04 profit
    function executeLiquidate(P calldata p) external returns (uint256 liquidatorProfitCollateralToken) {
        uint256 collateralRatio = state.collateralRatio(p.borrower);
        uint256 debtInCollateralToken = state.debtTokenAmountToCollateralTokenAmount(p.futureValue);
        uint256 liquidatorReward = Math.min(assignedCollateral - debtInCollateralToken, x);
        liquidatorProfitCollateralToken = debtInCollateralToken + liquidatorReward;
        uint256 collateralRemainder = assignedCollateral - liquidatorProfitCollateralToken;
        uint256 collateralRemainderCap = Math.mulDivDown(debtInCollateralToken, crLiquidation, PERCENT);
        collateralRemainder = Math.min(collateralRemainder, collateralRemainderCap);
        collateralToken.transferFrom(p.borrower, msg.sender, liquidatorProfitCollateralToken);
    }
    // 4. M-11 replacement swap fee
    function executeLiquidateWithReplacement(P calldata p) external returns (uint256 issuanceValue) {
        uint256 tenor = debtPosition.dueDate - block.timestamp;
        issuanceValue = Math.mulDivDown(futureValue, PERCENT, PERCENT + ratePerTenor);
        debtPosition.borrower = p.borrower;
        debtToken.mint(p.borrower, futureValue);
        borrowAToken.transferFrom(address(this), feeRecipient, liquidatorProfitBorrowToken);
    }
    // 3+5. M-09 health-after-action (no CR) + M-05/M-13 credit-sale
    function executeCompensate(P calldata p) external {
        uint256 amountToCompensate = Math.min(p.amount, creditPositionWithDebtToRepay.credit);
        state.reduceDebtAndCredit(debtPositionId, creditId, amountToCompensate);
        uint256 fragmentationFee = state.feeConfig.fragmentationFee;
        collateralToken.transferFrom(msg.sender, feeRecipient, fragmentationFee);
    }
    // 12. needs_context: liquidation mutator whose CR check is in an unresolved validate* helper
    function repayWithExternalCheck(P calldata p) external {
        validateSomething(p);
        debtToken.burn(p.borrower, p.amount);
        collateralToken.transferFrom(address(this), p.borrower, p.collateral);
    }
}

contract Negatives {
    // 6. plain ERC20 transfer
    function transfer(address to, uint256 amount) public returns (bool) { _b[msg.sender]-=amount; _b[to]+=amount; return true; }
    // 7. deposit (no liquidation terms)
    function deposit(uint256 amount) external { token.transferFrom(msg.sender, address(this), amount); }
    // 8. reward fee collection
    function claimRewards() external { reward.transfer(msg.sender, pending); }
    // 9. oracle getter
    function getPrice() external view returns (uint256) { return oracle.latestAnswer(); }
    // 10. admin setter (excluded even though "config")
    function updateConfig(uint256 crLiquidation, uint256 minTenor) external onlyOwner { riskConfig.crLiquidation = crLiquidation; }
    // 11. generic arithmetic with collateral term but no liquidation action (not name-gated)
    function computeCollateralValue(uint256 amount) public view returns (uint256) { return amount * price / 1e18; }
}
