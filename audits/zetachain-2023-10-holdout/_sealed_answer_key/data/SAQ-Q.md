
## Summary

### Low Risk Issues

no | Issue |Instances|
|-|:-|:-:|
| [L-01] | `receive()`/`payable fallback()` function does not authorize requests | 3 | 
| [L-02] | Consider implementing two-step procedure for updating protocol addresses | 4 | 
| [L-03] | `name()` is not a part of the ERC-20 standard | 1 | 
| [L-04] | `symbol()` is not a part of the ERC-20 standard | 1 | 
| [L-05] | `decimals()` is not a part of the ERC-20 standard | 1 | 
| [L-06] | External call recipient may consume all transaction gas | 3 | 
| [L-07] | Missing contract-existence checks before low-level calls | 5 | 
| [L-08] | Missing checks for `address(0x0)` in the constructor/initializer | 3 | 
| [L-09] | Missing checks for `address(0x0)` when updating `address` state variables | 1 | 

## Low Risk Issues

### [L-1] `receive()`/`payable fallback()` function does not authorize requests

Having no access control on the function (e.g. `require(msg.sender == address(weth))`) means that someone may send Ether to the contract, and have no way to get anything back out, which is a loss of funds. If the concern is having to spend a small amount of gas to check the sender against an immutable address, the code should at least have a function to rescue mistakenly-sent Ether.

```solidity
file: /contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

101    receive() external payable {}

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101C1-L101C34


```solidity
file: /contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

66    receive() external payable {}

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66C1-L66C34


```solidity
file: /contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

72    receive() external payable {}

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72C1-L72C34


### [L-2] Consider implementing two-step procedure for updating protocol addresses

A copy-paste error or a typo may end up bricking protocol functionality, or sending tokens to an address with no known private key. Consider implementing a two-step procedure for updating protocol addresses, where the recipient is set as pending, and must 'accept' the assignment by making an affirmative call. A straight forward way of doing this would be to have the target contracts implement [EIP-165](https://eips.ethereum.org/EIPS/eip-165), and to have the 'set' functions ensure that the recipient is of the right interface type.
```solidity
file: /contracts/evm/ERC20Custody.sol

80    function updateTSSAddress(address TSSAddress_) external onlyTSSUpdater {
        if (TSSAddress_ == address(0)) {
            revert ZeroAddress();
        }
        TSSAddress = TSSAddress_;
        emit UpdatedTSSAddress(TSSAddress_);
    }

    /**
     * @dev Update zeta fee
     * @param zetaFee_, new zeta fee
     */
    function updateZetaFee(uint256 zetaFee_) external onlyTSS {
        if (zetaFee_ == 0) {
            revert ZeroFee();
        }
        if (zetaFee_ > zetaMaxFee) {
            revert ZetaMaxFeeExceeded();
        }
        zetaFee = zetaFee_;
        emit UpdatedZetaFee(zetaFee_);
    }

    /**
     * @dev Change the ownership of TSSAddressUpdater to the Zeta blockchain TSS nodes.
     * Effectively, only Zeta blockchain validators collectively can update TSSAddress afterwards.
     */
    function renounceTSSAddressUpdater() external onlyTSSUpdater {
        if (TSSAddress == address(0)) {
            revert ZeroAddress();
        }
        TSSAddressUpdater = TSSAddress;
        emit RenouncedTSSUpdater(msg.sender);
    }

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L80C1-L113C6


```solidity
file: /contracts/evm/ZetaConnector.base.sol

128    function updateTssAddress(address tssAddress_) external {
        if (msg.sender != tssAddress && msg.sender != tssAddressUpdater) revert CallerIsNotTssOrUpdater(msg.sender);
        if (tssAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

        tssAddress = tssAddress_;

        emit TSSAddressUpdated(msg.sender, tssAddress_);
    }

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L128C3-L135C6


### [L-3] `name()` is not a part of the ERC-20 standard 

The `name()` function is not a part of the [ERC-20 standard](https://eips.ethereum.org/EIPS/eip-20), and was added later as an [optional extension](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/IERC20Metadata.sol). As such, some valid ERC20 tokens do not support this interface, so it is unsafe to blindly cast all tokens to this interface, and then call this function.

```solidity
file: /contracts/zevm/ZRC20.sol
  
83    function name() public view virtual override returns (string memory) {

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L83C1-L83C75

### [L-4] `symbol()` is not a part of the ERC-20 standard

The `symbol()` function is not a part of the [ERC-20 standard](https://eips.ethereum.org/EIPS/eip-20), and was added later as an [optional extension](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/IERC20Metadata.sol). As such, some valid ERC20 tokens do not support this interface, so it is unsafe to blindly cast all tokens to this interface, and then call this function.

```solidity
file: /contracts/zevm/ZRC20.sol

91    function symbol() public view virtual override returns (string memory) {
        return _symbol;

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L91C1-L92C24


### [L-5] `decimals()` is not a part of the ERC-20 standard

The `decimals()` function is not a part of the [ERC-20 standard](https://eips.ethereum.org/EIPS/eip-20), and was added later as an [optional extension](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/IERC20Metadata.sol). As such, some valid ERC20 tokens do not support this interface, so it is unsafe to blindly cast all tokens to this interface, and then call this function.

```solidity
file: /contracts/zevm/ZRC20.sol

99    function decimals() public view virtual override returns (uint8) {
        return _decimals;

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L99C1-L100C26


### [L-6] External call recipient may consume all transaction gas

There is no limit specified on the amount of gas used, so the recipient can use up all of the transaction's gas, causing it to revert. Use `addr.call{gas: <amount>}("")` or [this](https://github.com/nomad-xyz/ExcessivelySafeCall) library instead.

```solidity 
file: /contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

178        (bool sent, ) = destinationAddress.call{value: amountOut}("");

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178C1-L178C71


```solidity
file: /contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

152        (bool sent, ) = destinationAddress.call{value: amountOut}("");

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152C1-L152C71


```solidity
file: /contracts/zevm/ZetaConnectorZEVM.sol
 
96        (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96C1-L96C88


### [L-7]  Missing contract-existence checks before low-level calls

Low-level calls return success if there is no code present at the specified address. In addition to the zero-address checks, add a check to verify that `<address>.code.length > 0`

```solidity
file: /contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

203        uint256 amountOut = pancakeV3Router.exactInput(params);

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L203C1-L203C64


```solidity
file: /contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

115        address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);

130        uint256 amountOut = tridentRouter.exactInput(params);

150        IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L115C1-L115C82


```solidity
file: /contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

135        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L135C1-L135C96


### [L-8] Missing checks for `address(0x0)` in the constructor/initializer

```solidity
file: /contracts/zevm/ZRC20.sol

76        SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L76C1-L76C58


```solidity
file: /contracts/evm/ERC20Custody.sol

69        TSSAddress = TSSAddress_;
70        TSSAddressUpdater = TSSAddressUpdater_;

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L69C1-L70C48


```solidity
file: /contracts/zevm/ZetaConnectorZEVM.sol

79    constructor(address wzeta_) {
        wzeta = wzeta_;
    }

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79C1-L81C6


### [L-9] Missing checks for `address(0x0)` when updating `address` state variables

```solidity
file: /contracts/zevm/ZRC20.sol

///@audit ' SYSTEM_CONTRACT_ADDRESS ' is state variable.

271        SYSTEM_CONTRACT_ADDRESS = addr;

```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L271C1-L271C40


