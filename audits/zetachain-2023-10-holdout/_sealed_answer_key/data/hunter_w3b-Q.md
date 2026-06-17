# Low Risk and Non-Critical Issues

| Number |                                                                                 |
| :----: | :------------------------------------------------------------------------------ |
| [L-01] | Lack of minimum transaction amount validation enables denial of service attacks |
| [L-02] | Queue Processing Denial of Service                                              |
| [L-03] | SystemContract::depositAndCall function does not emit event on state changes    |
| [L-04] | Contracts are vulnerable to fee-on-transfer-token-related accounting issues     |
| [L-05] | Denial of Service Through Malicious Contract Deployments                        |
| [L-06] | receive() function does not authorize requests                                  |
| [L-07] | safeApprove() is deprecated                                                     |
| [N-08] | Decimal values like setGasPrice stored without proper handling of precision     |

## [L-01] Lack of minimum transaction amount validation enables denial of service attacks

The deposit() and withdraw() functions in the ERC20Custody and ZRC20 contracts do not validate the transaction amounts passed in. This allows deposits and withdrawals of extremely small amounts, even zero value transactions.

Large volumes of microtransactions or zero value transactions could be used to spam the contract and clog up the network, mounting a denial of service attack.

- Call deposit() or withdraw() with a very small or zero amount
- The transaction will succeed due to lack of amount validation

Enforcing a minimum transaction amount can prevent attackers from clogging the network with zero amount or dust transactions.

```solidity
File: contracts/evm/ERC20Custody.sol

165    function deposit(

193    function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L193

```solidity
File: contracts/zevm/ZRC20.sol

225    function deposit(address to, uint256 amount) external override returns (bool) {


256    function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225

## [L-02] Queue Processing Denial of Service

The ZRC20 and ERC20Custody contracts processes transactions sequentially from its queue without any protections like rate limiting or prioritization. This allows an attacker to flood the queue and disrupt legitimate usage.

An attacker submits a large number of deposit/withdrawal transactions to fill up the transaction queue.

This prevents legitimate users from having their transactions processed.

## [L-03] SystemContract::depositAndCall function does not emit event on state changes

The depositAndCall function updates balances/state by calling the deposit function on the IZRC20 contract. However, it does not emit any event to track these changes. This makes it harder for external callers/observers to know what the updated state is after a depositAndCall.

```solidity
File: contracts/zevm/SystemContract.sol

    function depositAndCall(
        zContext calldata context,
        address zrc20,
        uint256 amount,
        address target,
        bytes calldata message
    ) external {
        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
        if (target == FUNGIBLE_MODULE_ADDRESS || target == address(this)) revert InvalidTarget();

        IZRC20(zrc20).deposit(target, amount);
        zContract(target).onCrossChainCall(context, zrc20, amount, message);
    }
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67-L79

Add an event in depositAndCall that is emitted after the IZRC20 deposit, with relevant details like asset, amount, recipient etc. This will allow tracking changes to balances/state.

## [L-04] Contracts are possible vulnerable to fee-on-transfer-token-related accounting issues

Without measuring the balance before and after the transfer, there's no way to ensure that enough tokens were transferred, in the cases where the token has a fee-on-transfer mechanic. If there are latent funds in the contract, subsequent transfers will succeed.

```solidity
File: contracts/evm/ERC20Custody.sol

178            zeta.safeTransferFrom(msg.sender, TSSAddress, zetaFee);

181        asset.safeTransferFrom(msg.sender, address(this), amount);

197        IERC20(asset).safeTransfer(recipient, amount);
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L197

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

135        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);

159        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);

193        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L135

```solidity
File: ZetaTokenConsumerTrident.strategy.sol

108        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);

144        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);

175        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L108

```solidity
File:  contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

67        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);

103        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);

133        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);


```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L67-L68

## [L-05] Denial of Service Through Malicious Contract Deployments

The ImmutableCreate2Factory contract does not limit the number of contracts that can be deployed. This allows an attacker to bombard the contract with bogus create2 calls, consuming large amounts of storage over time and increasing gas costs for legitimate users. Once storage usage grows out of bounds, the contract becomes unusable.

```solidity
File: contracts/evm/tools/ImmutableCreate2Factory.sol

contract ImmutableCreate2Factory {

```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L22

Deploy a simple contract that calls safeCreate2() or safeCreate2Internal() in a loop millions of times with randomly generated salts/code. Monitor increasing storage usage over time via Etherscan or other means.

## [L-06] receive() function does not authorize requests

Having no access control on the function (e.g. require(msg.sender == address(weth))) means that someone may send Ether to the contract, and have no way to get anything back out, which is a loss of funds. If the concern is having to spend a small amount of gas to check the sender against an immutable address, the code should at least have a function to rescue mistakenly-sent Ether.

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

101    receive() external payable {}
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

66    receive() external payable {}
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

72    receive() external payable {}
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72

## [L-07] safeApprove() is deprecated

[Deprecated](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/bfff03c0d2a59bcd8e2ead1da9aed9edf0080d05/contracts/token/ERC20/utils/SafeERC20.sol#L38-L45) in favor of safeIncreaseAllowance() and safeDecreaseAllowance(). If only setting the initial allowance to the value that means infinite, safeIncreaseAllowance() can be used instead. The function may currently work, but if a bug is found in this version of OpenZeppelin, and the version that you're forced to upgrade to no longer has this function, you'll encounter unnecessary delays in porting and testing replacement contracts.

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

136         IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount);

160        IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);

194        IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L136

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

109        IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount);

145        IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);

176        IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L109

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

68        IERC20(inputToken).safeApprove(address(uniswapV2Router), inputTokenAmount);

104        IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);

134        IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L68

## [N-08] Decimal values like setGasPrice stored without proper handling of precision

The SystemContract stores values like SetGasPrice as uint256 without considering decimal precision. Over many transactions, small rounding errors in arithmetic could accumulate and lead to loss of funds.Use a decimal library to handle prices and amounts with a fixed number of decimal places. Refactor functions to use the decimal type instead of uint256.

```solidity
File: contracts/zevm/SystemContract.sol

    function setGasPrice(uint256 chainID, uint256 price) external {
        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
        gasPriceByChainId[chainID] = price;
        emit SetGasPrice(chainID, price);
    }
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L123-L127
