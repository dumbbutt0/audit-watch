## [NC-1] Wrong comment on the ZetaTokenConsumerPancakeV3 contract comment.

The comment on the ZetaTokenConsumerPancakeV3 contract is incorrect. The comment described the contract as Uniswap strategy while it Pancakeswap Strategy
```
**
 * @dev Uniswap V3 strategy for ZetaTokenConsumer //@audit-info It is Pancake.
 */
contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
File: https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L54

## [LC-1] The ZetaConnectorBase contract should be an asbstract contract.

The ZetaConnectorBase contract should be an asbstract contract with the `send(...)`, `onReceive(...)` and `onRevert(...)` made abstract function so the other contracts like the `ZetaConnectorEth` and `ZetaConnectorNonEth` that inherit `ZetaConnectorBase` abstract contract are forced to implement the above 3 functions without mistake in spelling of the functions.

Making `ZetaConnectorBase` an abstract contract will help linting tools detect functions that needed to be implemented in every inheriting solid contract.
It also ensures that `ZetaConnectorBase` is not mistakenly deployed alone.

File: https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15

## [L-2] The `hasZetaLiquidity()` function of the ZetaTokenConsumerTrident.strategy.sol always return a boolean false.

The `hasZetaLiquidity()` code is not implemented so it currently always return `false`.
```
function hasZetaLiquidity() external view override returns (bool) {
        //@TODO: Implement
        return false;//@audit-issue DOS.
    }
```
File: https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203C5-L206C6

## [L-3] Use a more recent pragma solidity version and Openzeppelin version
The project currently uses `pragma solidity 0.8.7;`. it is important to use a more recent compiler version since it will have more bug fixes. 
0.8.19 recommended.
```
pragma solidity 0.8.7;
```
Use a more recent version of Openzeppelin. 5.0 recommended.
```
"@openzeppelin/contracts": "^4.8.3",
```
Files: All files.
According to solidity docs: "Always use the latest version of the compiler to be notified about all recently introduced warnings."
link: https://docs.soliditylang.org/en/latest/security-considerations.html#take-warnings-seriously

## [L-3] The Uniswap.sol and UniswapPeriphery.sol files have the same empty contract with the same contract names.

The two files above have the same contract names and the contract is empty.
```
contract UniswapImports {}
```
This may indicate an unfinished work so either implement them or remove them if they are not needed.

## [L-4] Emit `SetWZETA` event when is set in the constructor of the ZetaConnectorZEVM.sol contract.

```
vent SetWZETA(address wzeta_);
constructor(address wzeta_) {
        wzeta = wzeta_;
    }
```
File: https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L77C5-L81C6

## [L-5] Specify names of modules to import individually instead of global imports
Use 
```
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
```
instead of 
```
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
```

Files: All files

## [L-6] Consider implementing 2 step procedure for updating protocol addresses
The `updateTSSAddress` should use 2 step procedure
```
/**
     * @dev Update the TSSAddress in case of Zeta blockchain validator nodes churn.
     * @param TSSAddress_, new tss address.
     */
    function updateTSSAddress(address TSSAddress_) external onlyTSSUpdater {
        if (TSSAddress_ == address(0)) {
            revert ZeroAddress();
        }
        TSSAddress = TSSAddress_;
        emit UpdatedTSSAddress(TSSAddress_);
    }
```
File: https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L80C5-L86C6

Update Pauser address should use 2 step procedure

```
 function updatePauserAddress(address pauserAddress_) external onlyPauser {
        if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

        pauserAddress = pauserAddress_;

        emit PauserAddressUpdated(msg.sender, pauserAddress_);
    }
```
File: https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L117C5-L123C6

## [L-7] No contract existence check before yul .call function.
According to Solidity, Yul calls to non-existent contracts with return true so it is important to implement a contract existence check if the address is not an EOA.
link: https://docs.soliditylang.org/en/latest/units-and-global-variables.html#members-of-address-types

```
(bool sent, ) = destinationAddress.call{value: amountOut}("");
        if (!sent) revert ErrorSendingETH();

```
Files: 
- https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178C9-L180C1
- https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152C9-L153C45

## [L-8] Allow TSSAddress to withdraw any type of token not only the whitelisted address
The `withdraw(...)` function of ERC20Custody.sol contract will revert if TSS tries to withdraw other tokens other than the whitelisted token. It is important to note that the ERC20Custody.sol may end up receiving several other tokens are not whitelisted. Some of these due to human error directly sent to the ERC20Custody.sol.
```
function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
        if (!whitelisted[asset]) {//@audit-issue does not check for pause.
            revert NotWhitelisted();
        }
        IERC20(asset).safeTransfer(recipient, amount);//@audit TSS can drain all the user funds.
        emit Withdrawn(recipient, asset, amount);
    }
```
The withdraw function can also serve as a `rescue token` function.
File: https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L193C5-L199C6

## [L-9] TSS can withdraw tokens after the ERC20Custody.sol contract is paused.

Implement the `whenNotPaused` check on the `withdraw` function of ERC20Custody.sol so that when the contract is paused, TSS will not be able to withdraw.

```
function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
        if (!whitelisted[asset]) {//@audit-issue does not check for pause.
            revert NotWhitelisted();
        }
        IERC20(asset).safeTransfer(recipient, amount);//@audit TSS can drain all the user funds.
        emit Withdrawn(recipient, asset, amount);
    }
```

File: https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L193C5-L199C6

