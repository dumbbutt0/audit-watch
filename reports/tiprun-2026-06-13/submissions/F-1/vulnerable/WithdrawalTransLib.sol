// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "../../position/IPositionManager.sol";
import "../ILoadingZone.sol";
import "../../account/IAccountManager.sol";
import "../../../utils/SignaturesLib.sol";
import "../../../utils/EIP712DomainLib.sol";
import "../../signer/ISignerManager.sol";
import "../../signer/SignerPermissions.sol";
import "../../risk/IBalanceCheck.sol";
import "../../../Constants.sol";

struct Withdrawal {
    uint64 from; // Withdraw request sender account ID
    address toAddress; // Withdraw recipient address, TODO: allow another withdrawal address? or force to owner address?
    int256 amount; // Withdraw  amount
    uint256 nonce;
    bytes signature; // Signature of the withdrawal
}

/**
 * @title WithdrawalTransLib
 * @dev Library for handling withdrawals to specified positions
 */
library WithdrawalTransLib {
    bytes32 public constant WITHDRAWAL_TYPEHASH =
        keccak256("Withdrawal(uint64 from,address toAddress,int256 amount,uint256 nonce)");

    function process(
        Withdrawal memory self,
        IPositionManager position,
        IAccountManager accountManager,
        ILoadingZone loadingZone,
        ISignerManager signerManager,
        IBalanceCheck balanceCheck,
        address verifyingContract
    ) public {
        require(self.amount > 0, "WithdrawalTransLib: amount must be greater than 0");
        require(self.from != 0, "WithdrawalTransLib: withdrawal account ID is 0");
        require(self.toAddress != address(0), "WithdrawalTransLib: to address is 0");
        address fromAddress = accountManager.getAddressByAccountId(uint64(self.from));
        require(fromAddress != address(0), "WithdrawalTransLib: withdrawal address is not registered");
        // Balance-safety delegated to the IBalanceCheck capability provider.
        balanceCheck.validateWithdrawal(uint64(self.from), self.amount);

        bytes32 messageHash = getWithdrawalHash(self, block.chainid, verifyingContract);
        address signer = SignaturesLib.recoverSigner(messageHash, self.signature);
        require(
            signerManager.checkSignerPermissionsAndNonce(
                self.from, signer, self.nonce, SignerPermissions.ALLOW_WITHDRAW
            ),
            "WithdrawalTransLib: invalid permissions or nonce"
        );
        // Update position (reduce user's balance in the system)
        position.updatePositionInDict(self.from, -self.amount, NO_SYNTHETIC_DELTA_ASSET_ID, 0);

        require(
            loadingZone.processWithdraw(self.toAddress, uint256(self.amount)),
            "WithdrawalTransLib: LoadingZone processing failed"
        );
    }

    function getWithdrawalHash(Withdrawal memory self, uint256 chainId, address verifyingContract)
        public
        pure
        returns (bytes32)
    {
        bytes32 structHash =
            keccak256(abi.encode(WITHDRAWAL_TYPEHASH, self.from, self.toAddress, self.amount, self.nonce));
        return EIP712DomainLib.toTypedDataHash(structHash, chainId, verifyingContract);
    }
}
