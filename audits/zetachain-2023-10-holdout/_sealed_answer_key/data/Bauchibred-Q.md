QA Report

## Table of Contents

| Issue ID                                                                                                                                                                   | Description                                                                                                                                                   |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [QA-01](#qa-01-tokens-that-can-be-deposited-to-zeta-need-to-first-be-whitelisted-but-there-is-no-mechanism-incase-the-acess-to-the-underlying-address-of-an-asset-changes) | Tokens that can be deposited to Zeta need to first be whitelisted, but there is no mechanism in case the access to the underlying address of an asset changes |
| [QA-02](#qa-02-protocol-uses-deprecated-transfer-to-send-native-tokens)                                                                                                    | Protocol uses deprecated `.transfer()` to send native tokens                                                                                                  |
| [QA-03](#qa-03-sqrtpricelimitx96-shouldnt-be-hardcoded-to-0)                                                                                                               | `sqrtPriceLimitX96` shouldn't be hardcoded to 0                                                                                                               |
| [QA-04](#qa-04-protocol-should-implement-a-pauser-and-unpauser-address)                                                                                                    | Protocol should implement a pauser & unpauser address                                                                                                         |
| [QA-05](#qa-05-complete-measures-are-not-taken-to-ensure-that-the-transfer-of-eth-to-destinationaddress-always-goes-through)                                               | Complete measures are not taken to ensure that the transfer of `ETH` to `destinationAddress` always goes through                                              |
| [QA-06](#qa-06-the-getlockedamount-should-not-exist-in-zetanonethinterface-since-tokens-only-get-locked-in-the-eth-connector)                                              | The `getLockedAmount()` should not exist in `ZetaNonEthInterface` since tokens only get locked in the Eth connector                                           |
| [QA-07](#qa-07-the-trident-consumer-strategy-expects-a-uniswap-router-while-constructing-where-as-it-should-be-trident-router)                                             | The trident consumer strategy expects a Uniswap router while constructing whereas it should be Trident router                                                 |
| [QA-08](#qa-08-protocol-shouldnt-use-uniswapv2-pool-for-all-chains-to-make-swaps)                                                                                          | Protocol shouldn't use `uniswapv2` pool for all chains to make swaps                                                                                          |
| [QA-09](#qa-09-some-instances-of-typos)                                                                                                                                    | Some instances of typos                                                                                                                                       |

## QA-01 Tokens that can be deposited to zeta need to first be whitelisted, but there is no mechanism incase the acess to the underlying address of an asset changes

### Proof of Concept

Take a look at [ERC20Custody.sol#L36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L36)

```solidity
    /// @notice Mapping of whitelisted token => true/false.
    mapping(IERC20 => bool) public whitelisted;
```

Note that tokens are being whitelisted before they can get deposited, but the only thing that protocol doesn't take to note is that, some tokens can have access to their underlying addresses revoked, which would mean that if these tokens exist in the protocol they can no longer be [withdrawn](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L187-L199), the new address could get whitelisted later on, but tokens that are already in the Custody contract would be inacessible.

To explain a bit further, it's no news that some ERC20 tokens exist with multiple entry points (also known as double entry tokens or two address tokens), now due to a reported [bug case](https://blog.openzeppelin.com/compound-tusd-integration-issue-retrospective) for one of the popular token that implements this feature, namely TUSD, the protocol curbed access from one of it's addresses. In addition, it is not unrealistic to expect that an upgradeable collateral token like USDT could become a double-entrypoint token in the future, so this must also be considered.

How this works is that if the legacy token address of the double entry point token now blocks the access of its logic from the second token address, then attempting to withdraw would not work cause the the right address was not whitelisted and an attempt to withdraw would revert.

### Impact

> Medium/low cause where as it would be detrimental to protocol one can argue that this would count as admin misconfiguration for whitelisting the double entry token in the first place.

This would not only make it impossible to send these tokens to Zeta but also all other previously sent tokens would be stuck in the protocol since an attempt to get these tokens via this address would now revert... essentially a DOS and also broken logic for core functionalities.

### Recommended Mitigation Steps

Hard one to recommend a fix for cause a popular fix to this bug case would limit the flexibility of the Zeta protocol, that's by clearly not whitelisting such tokens, but they would still be a need to ensure that upgradeable tokens being supported are also kept in check, alternatively Do not rely on the token address in the internal accounting.

## QA-02 Protocol uses deprecated `.transfer()` to send native tokens

### Proof Of Concept

Take a look at [WZETA.sol#L25-L30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol#L25-L30)

```solidity

    function withdraw(uint wad) public {
        require(balanceOf[msg.sender] >= wad);
        balanceOf[msg.sender] -= wad;
        //@audit
        msg.sender.transfer(wad);
        Withdrawal(msg.sender, wad);
    }
```

As seen this function is meant to be used by users when they are trying to withdraw their WZETA tokens, but this attempt to transfer is somewhat since it uses `transfer()` to send the native token

Now it's well known that the original `transfer` used to send native tokens uses a fixed stipend 2300 gas. This was used to "prevent reentrancy". However this limits the protocol's ability to interact with others contracts that would need more than that to process their transactions, coupled with the fact that this has been deprecated and would be certain to lead to faulty nuances in the case where a user has a fallback implementation that rrequires more than 2300

A good article that covers more details regarding this can be found here: https://consensys.net/diligence/blog/2019/09/stop-using-soliditys-transfer-now/.

### Impact

Usage of this could cause some revertions to occur for contracts that require more gas to process this recieval of tokens

### Recommendation

Use `.call()` instead of `transfer` to send native tokens. Also the return value of this attempt to transfer must be checked to see if sending the token was successful or not.

## QA-03 sqrtPriceLimitX96 shouldn't be hardcoded to0

### Impact

QA, since there is already a `minAmountOut` slippage applied, but Uniswap V3 introduce the concept of centralized liquidity with price range. Setting sqrtPriceLimitX96 dynamically can help protect against price impact and protect user from unexpected from slippage.

Source: https://ethereum.stackexchange.com/questions/121178/how-to-trade-directly-with-uniswap-v3-pool-instead-of-through-router

### Proof of Concept

Using this search command: [`https://github.com/search?q=repo%3Acode-423n4%2F2023-11-zetachain+sqrtPriceLimitX96+NOT+language%3AGo+NOT+language%3ATypeScript&type=code`](https://github.com/search?q=repo%3Acode-423n4%2F2023-11-zetachain+sqrtPriceLimitX96+NOT+language%3AGo+NOT+language%3ATypeScript&type=code) we can see that there are multiple instances of "sqrtPriceLimitX96: 0" in the protcol's codebase, but [here is one of them from the pancakeswap strategy to use as an example](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103-L124)

```solidity
    function getZetaFromEth(
        address destinationAddress,
        uint256 minAmountOut
    ) external payable override returns (uint256) {
        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (msg.value == 0) revert InputCantBeZero();

        ISwapRouterPancake.ExactInputSingleParams memory params = ISwapRouterPancake.ExactInputSingleParams({
            tokenIn: WETH9Address,
            tokenOut: zetaToken,
            fee: zetaPoolFee,
            recipient: destinationAddress,
            amountIn: msg.value,
            amountOutMinimum: minAmountOut,
            //@audit
            sqrtPriceLimitX96: 0
        });

        uint256 amountOut = pancakeV3Router.exactInputSingle{value: msg.value}(params);

        emit EthExchangedForZeta(msg.value, amountOut);
        return amountOut;
    }
```

Evidently, sqrtPriceLimitX96 has been hardcoded to `0` while attempting the swap, but this implementation is somewhat flawed since in production `sqrtPriceLimitX96` can be used to set the limit for the price the swap will push the pool to, which can help protect against price impact or for setting up logic in a variety of price-relevant mechanisms.

### Recommended Mitigation Steps

Allow users to pass in the parameter sqrtPriceLimitX96

## QA-04 Protocol should implement a pauser & unpauser address

### Proof of Concept

Take a look at [ZetaConnectorBase.sol]()

```solidity
    /**
     * @dev Multisig contract to pause incoming transactions.
     * The responsibility of pausing outgoing transactions is left to the protocol for more flexibility.
     */

    address public pauserAddress;
```

### Impact

Potentially unpausing the protocol when everything is not okay, sinceis no need to pass the threshold of required signers

### Recommended Mitigation Steps

A popular apporach is to have a different pausing and unpausing route, i.e each addresses of the multisig could be given a pauser role and in the case of a black swan event any one with this role can pause the protocol, and for unpausing this can then go via the multisig as they would make due process and ensure that everything is okay before unpausing the protocol.

Also current implementation of having only one pauser is risky as an emergency could occur and pauser might not be availaible, lastly the multisig should also be given the ability to change the pauser address.

## QA-05 Complete measures are not taken to ensure that the transfer of `ETH` to `destinationAddress` always goes through

### Proof of Concept

Take a look at [getEthFromZeta()]()

```solidity
    function getEthFromZeta(
        address destinationAddress,
        uint256 minAmountOut,
        uint256 zetaTokenAmount
    ) external override returns (uint256) {
        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (zetaTokenAmount == 0) revert InputCantBeZero();

        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
        IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);

        ISwapRouterPancake.ExactInputSingleParams memory params = ISwapRouterPancake.ExactInputSingleParams({
            tokenIn: zetaToken,
            tokenOut: WETH9Address,
            fee: zetaPoolFee,
            recipient: address(this),
            amountIn: zetaTokenAmount,
            amountOutMinimum: minAmountOut,
            sqrtPriceLimitX96: 0
        });

        uint256 amountOut = pancakeV3Router.exactInputSingle(params);

        WETH9(WETH9Address).withdraw(amountOut);

        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
    //@audit QA the destination address should be wrapped in a payable https://github.com/code-423n4/2023-10-party-findings/issues/146
        (bool sent, ) = destinationAddress.call{value: amountOut}("");
        if (!sent) revert ErrorSendingETH();

        return amountOut;
    }

```

As seen, this function uses the `.call()` method to send the ETH to `destinationAddress` after the swap, but this transaction could fail and contract assumes that it goes through, this is cause there is no account existence check applied to `destinationAddress` and solidity returns true for low-level calls to non-existent addresses return true, additionally the `destinationAddress` has not been wrapped in a `payable`

### Impact

Low, since this seems to be user error, but currently assumptions are being made that the eth was susccessfully transferred, where as there is a possibility that the tokens were not sent to the destination.

### Recommended Mitigation Steps

Add a contract existence check and also wrap the call in a `payable`.

## QA-06 The `getLockedAmount()` should not exist in `ZetaNonEthInterface` since tokens only get locked in the Eth connector

### Impact

Better code structure and and smaller contract size

### Proof of Concept

Take a look at [getLockedAmount()]()

```solidity
    function getLockedAmount() external view returns (uint256) {
        return ZetaNonEthInterface(zetaToken).balanceOf(address(this));
    }

```

### Recommended Mitigation Steps

Since `ZetaNonEthInterface` wouldn't implement this function it should be removed

## QA-07 The trident consumer strategy expects a uniswap router while constructing where as it should be trident router

### Impact

### Proof of Concept

Take a look at [ZetaTokenConsumerTrident.strategy.sol#L45-L57](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45-L57)

```solidity
    constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {
        if (
            zetaToken_ == address(0) ||
            uniswapV3Router_ == address(0) ||
            WETH9Address_ == address(0) ||
            poolFactory_ == address(0)
        ) revert ZetaCommonErrors.InvalidAddress();

        zetaToken = zetaToken_;
        //@audit
        tridentRouter = IPoolRouter(uniswapV3Router_);
        poolFactory = ConcentratedLiquidityPoolFactory(poolFactory_);
        WETH9Address = WETH9Address_;
    }
```

Probably an innocent copy paste error, but as seen it expects a uniswap router while constructing where as it should be trident router

### Recommended Mitigation Steps

Correctly pass the router that's needed

## QA-08 Protocol shouldn't use `uniswapv2` pool for all chains to make swaps

### Proof of Concept

Take a look at [SystemContract.sol#L27-L29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L27-L29)

```solidity
    // @dev: Map to know uniswap V2 pool of ZETA/ZRC20 given a chain id. This refer to the build in uniswap deployed at genesis.
    mapping(uint256 => address) public gasZetaPoolByChainId;
```

### Impact

As seen, protocol has a mapping and attaches it to the uniswap V2 pool for `ZETA/ZRC20` for every given chain Id to make swaps, this approch could be problematic, multiple ideas exist but one would be the case where this uniswap pool doesn't exist on these chains or doesn't have enough liquidity.

### Recommended Mitigation Steps

Allow other pools to be attached to one specific `ERC20` against `ZRC20`.

## QA-09 Some instances of typos

### Impact

Better code structure and documentation.

### Proof of Concept

Take a look at []()

```solidity
    /// @notice Custom SystemContract errors. @audit i
    event SystemContractDeployed();
    event SetGasPrice(uint256, uint256);
    event SetGasCoin(uint256, address);
    event SetGasZetaPool(uint256, address);
    event SetWZeta(address);
    event SetConnectorZEVM(address);
```

Change to: `@notice Custom SystemContract events`.

Additionally multiple instances of `Etherum` being used instead `Ethereum`

From `ZRC20.sol`, `recipiuent` should be `recipient`

```solidity
    /**
     * @dev Returns ZRC20 balance of an account.
     * @param recipient, recipiuent address to which transfer is done.@audit
     * @return true/false if transfer succeeded/failed.
     */
```

```diff
    /**
     * @dev Deposits corresponding tokens from external chain, only callable by Fungible module.
+     // @audit info add that it's callable by SYSTEM_CONTRACT_ADDRESS too
     * @param to, recipient address.
     * @param amount, amount to deposit.
     * @return true/false if succeeded/failed.
     */
```

### Recommended Mitigation Steps

Apply suggested fixes.
