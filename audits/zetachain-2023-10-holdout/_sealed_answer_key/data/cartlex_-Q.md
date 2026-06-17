| ID | Description | Severity |
| :-: | - | :-: |
| [L-01](#l-01-updategaslimit-function-can-set-gaslimit-to-zero-value) | `updateGasLimit` function can set `GAS_LIMIT` to zero value. | Low |
| [L-02](#l-02-zetafee-can-be-zero-or-exceed-zetamaxfee-in-construction) | `zetaFee` can be zero or exceed `zetaMaxFee` in construction. | Low |
| [L-03](#l-03-unusedempty-receive) | Unused/empty receive. | Low |
| [L-04](#l-04-setgasprice-can-set-price-to-zero-value) | `setGasPrice()` can set `price` to zero value. | Low |
| [L-05](#l-05-consider-implementing-two-step-procedure-for-updating-protocol-addresses) | Consider implementing two-step procedure for updating protocol addresses | Low |
| [L-06](#l-06-any-token-can-be-set-as-gascoin-via-setgascoinzrc20) | Any token can be set as `GasCoin` via `setGasCoinZRC20()`. | Low |
| [L-07](#l-07-missing-zero-address-checks) |  Missing zero address checks. | Low |
| [L-08](#l-08-add-require-to-setmaxsupply-function) | Add require to `setMaxSupply()` function. | Low |
| [L-09](#l-09-lack-of-checks-in-getpair-functions) | Lack of checks in `getPair()` functions. | Low |
| [NC-01](#nc-01-unused-lines-of-code) | Unused lines of code | Non-critical |
| [NC-02](#nc-02-two-instances-of-izrc20-interface) | Two instances of IZRC20 interface. | Non-critical |
| [NC-03](#nc-03-function-with-todo) | Function with `@TODO`. | Non-critical |
| [NC-04](#nc-04-typos) | Typos. | Non-critical |

# [L-01] `updateGasLimit` function can set `GAS_LIMIT` to zero value.
## Description
In `ZRC20.sol` contract `updateGasLimit()` function can set `GAS_LIMIT` value.

```solidity
function updateGasLimit(uint256 gasLimit) external onlyFungible {
    GAS_LIMIT = gasLimit;
    emit UpdatedGasLimit(gasLimit);
}
```
https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L279-L282


This value then used in `withdrawGasFee()` function when `gasFee` is calculating. If `GAS_LIMIT` is equal to zero, only `PROTOCOL_FLAT_FEE` is accounted for `gasFee`.

```solidity
uint256 gasFee = gasPrice * GAS_LIMIT + PROTOCOL_FLAT_FEE; 
```

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L245


`gasFee` then used in `withdraw()` function, hence `FUNGIBLE_MODULE_ADDRESS` will receive less fee, or even zero, if `PROTOCOL_FLAT_FEE` is also equal to zero.

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L258-L259


## Recommended Mitigation Steps
Consider to restrict `FUNGIBLE_MODULE_ADDRESS` from setting `gasLimit` to zero value.

```diff
function updateGasLimit(uint256 gasLimit) external onlyFungible {
++  if (gasLimit == 0) revert InvalidGasLimit();
    GAS_LIMIT = gasLimit; 
    emit UpdatedGasLimit(gasLimit);
}
```

# [L-02] `zetaFee` can be zero or exceed `zetaMaxFee` in construction.

## Description
It is assumed that `zetaFee` should be less or equal to `zetaMaxFee` since we can see the check in `updateZetaFee()` function.

```solidity
if (zetaFee_ > zetaMaxFee) {
    revert ZetaMaxFeeExceeded();
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L96-L97


Hovewer, `zetaFee` parameter still can be set to `zero` value or can be set to a value that is `exceed` `zetaMaxFee` in the `constructor` of the contract.

```solidity
zetaFee = zetaFee_;
```

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L74


Moreover, if `zetaFee` value is set to zero, when `deposit()` function is used the contract will non receieve any fee.

```solidity
if (zetaFee != 0 && address(zeta) != address(0)) {
    zeta.safeTransferFrom(msg.sender, TSSAddress, zetaFee);
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L177-L179

## Recommended Mitigation Steps
To restrict maximum `zetaFee_` bound consider to implement the following changes:

```diff
constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
++  if (zetaFee_ > zetaMaxFee_) revert ZetaMaxFeeExceeded();
++  if (zetaFee_ == 0) revert ZeroFee();
    TSSAddress = TSSAddress_;
    TSSAddressUpdater = TSSAddressUpdater_;
    zetaFee = zetaFee_;
    zeta = zeta_;
    zetaMaxFee = zetaMaxFee_;
}
```

# [L-03] Unused/empty receive.

## Description
The receive function is not restricted to WETH token transfers, which could lead to unexpected token transfers to a smart contract. The unrestricted receive function may allow users to send native tokens to the contract. This could result in the undesired accumulation of tokens within the contract, making them permanently locked and inaccessible to the intended recipients.

```solidity
receive() external payable {}
```

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72


Same issue exist in `ZetaTokenConsumerUniV3.strategy.sol`,

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101


in `ZetaTokenConsumerTrident.strategy.sol`,

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66

## Recommended Mitigation Steps
To mitigate this issue, consider to implement a check within the receive function to ensure that only WETH token transfers are allowed.

```diff
receive() external payable {
++  if (msg.sender != WETH9Address) revert OnlyWETH9();
}
```

# [L-04] `setGasPrice()` can set `price` to zero value.

## Description
In `SystemContract.sol` FUNGIBLE_MODULE_ADDRESS can set gas price value of specific chainId to zero value.

```solidity
function setGasPrice(uint256 chainID, uint256 price) external {
    if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
    gasPriceByChainId[chainID] = price;
    emit SetGasPrice(chainID, price);
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L123-L127


However, when `withdrawGasFee()` function is used it can revert if gas price is equal to zero value.

```solidity
function withdrawGasFee() public view override returns (address, uint256) {
    address gasZRC20 = ISystem(SYSTEM_CONTRACT_ADDRESS).gasCoinZRC20ByChainId(CHAIN_ID);
    if (gasZRC20 == address(0)) {
        revert ZeroGasCoin();
    }
    uint256 gasPrice = ISystem(SYSTEM_CONTRACT_ADDRESS).gasPriceByChainId(CHAIN_ID);
    if (gasPrice == 0) {
        revert ZeroGasPrice();
    }
    uint256 gasFee = gasPrice * GAS_LIMIT + PROTOCOL_FLAT_FEE;
    return (gasZRC20, gasFee);
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L241-L243


## Recommended Mitigation Steps
Consider to restrict setting price to zero value in `setGasPrice()` function.

```diff
function setGasPrice(uint256 chainID, uint256 price) external {
    if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
++  if (price == 0) revert InvalideGasPrice(); 
    gasPriceByChainId[chainID] = price;
    emit SetGasPrice(chainID, price);
}
```

# [L-05] Consider implementing two-step procedure for updating protocol addresses.

## Description
A copy-paste error or a typo may end up bricking protocol functionality, or sending tokens to an address with no known private key. Consider implementing a two-step procedure for updating protocol addresses, where the recipient is set as pending, and must 'accept' the assignment by making an affirmative call. 

Issues exist in `ZetaConnector.base.sol` contract:

```solidity
pauserAddress = pauserAddress_;
```

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L117-L123


```solidity
tssAddress = tssAddress_;
```

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L128-L135


In `ZRC20` contract:

```solidity
SYSTEM_CONTRACT_ADDRESS = addr;
```

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L271


# [L-06] Any token can be set as `GasCoin` via `setGasCoinZRC20()`.

## Description
In `SystemContract.sol` to set the token in which gas will be paid `setGasCoinZRC20()` function can be used.

```solidity
function setGasCoinZRC20(uint256 chainID, address zrc20) external {
    if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
    gasCoinZRC20ByChainId[chainID] = zrc20;
    emit SetGasCoin(chainID, zrc20);
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L134-L138


Inside `ZRC20.sol` contract the value of gas token used in `withdraw()` function. 

```solidity
(address gasZRC20, uint256 gasFee) = withdrawGasFee();
```

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L257


Then, it checks if `gasZRC20` is an `IZRC20` interface implementer and transfers an amount of `fee` to `FUNGIBLE_MODULE_ADDRESS`.

```solidity
if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
    revert GasFeeTransferFailed();
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L258-L260C10


In this place a revert could happen if token passed as input parameter to `setGasCoinZRC20()` function is not implemeter of `IZRC20` interface. Hence `withdraw()` function can't be used until gas token changed.

Moreover, it's better to check that `gasZRC20` has enum type of `Gas`.

## Recommended Mitigation Steps
To mitigate this issue, I would recommended to add `COIN_TYPE` function to `IZRC20` interface and to implement the next check.

```diff
function setGasCoinZRC20(uint256 chainID, address zrc20) external {
    if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
++  if (IZRC20(zrc20).COIN_TYPE() != CoinType.Gas) revert NotGasCoin();
    gasCoinZRC20ByChainId[chainID] = zrc20; 
}
```


# [L-07] Missing zero address checks.

## Description
There are some missing checks of zero address.

In `ERC20Custody.sol`.

```solidity
constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
        TSSAddress = TSSAddress_; // @audit miss zero address check
        TSSAddressUpdater = TSSAddressUpdater_; // @audit miss zero address check
        zetaFee = zetaFee_;
        zeta = zeta_; // @audit miss zero address check
        zetaMaxFee = zetaMaxFee_;
    }
```

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L69-L70

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L72


```solidity
function whitelist(IERC20 asset) external onlyTSS { // @audit miss zero address check
    whitelisted[asset] = true;
    emit Whitelisted(asset);
}
```


https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L144


```solidity
function unwhitelist(IERC20 asset) external onlyTSS { // @audit miss zero address check
    whitelisted[asset] = false;
    emit Unwhitelisted(asset);
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L153-L156


In `SystemContract.sol` contract:

```solidity
constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {
    if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
    wZetaContractAddress = wzeta_; // @audit miss zero address check
    uniswapv2FactoryAddress = uniswapv2Factory_; // @audit miss zero address check
    uniswapv2Router02Address = uniswapv2Router02_; // @audit miss zero address check
    emit SystemContractDeployed();
```

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L53-L55


```solidity
function setGasCoinZRC20(uint256 chainID, address zrc20) external {
    if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
    gasCoinZRC20ByChainId[chainID] = zrc20; // @audit miss zero address check
    emit SetGasCoin(chainID, zrc20);
}
```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L136


In `ZetaConnectorZEVM.sol` contract:
```solidity
constructor(address wzeta_) {
    wzeta = wzeta_; // @audit miss zero address check
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79


```solidity
function setWzetaAddress(address wzeta_) external {
    if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert OnlyFungibleModule();
    wzeta = wzeta_; // @audit miss zero address check
    emit SetWZETA(wzeta_);
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L116


In `ZRC20.sol` contract:

```solidity
SYSTEM_CONTRACT_ADDRESS = systemContractAddress_; // @audit miss zero address check
```

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L76


```solidity
function updateSystemContractAddress(address addr) external onlyFungible {
    SYSTEM_CONTRACT_ADDRESS = addr; // @audit miss zero address check
    emit UpdatedSystemContract(addr);
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L271


## Recommended Mitigation Steps
Consider to implement zero address checks.


# [L-08] Add require to `setMaxSupply()` function.

## Description
It is possible to set `maxSupply` to any value using `setMaxSupply()` function.

This variable used in `onReceive()` and `onRevert()` functions

```solidity
if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
```

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L69


```solidity
if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
```

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L96-L97


If `maxSupply` set to value less than `totalSupply()` these functions will always revert.

## Recommended Mitigation Steps
Consider to implement the next changes is `setMaxSupply()` function.

```diff
function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
++  require(maxSupply_ >= ZetaNonEthInterface(zetaToken).totalSupply(), "invalid supply");
    maxSupply = maxSupply_;
    emit MaxSupplyUpdated(msg.sender, maxSupply_);
}
```


# [L-09] Lack of checks in `getPair()` functions.

## Description
In `ZetaTokenConsumerTrident.strategy.sol` contract there is a `getPair()` function which sort tokens.

```solidity
function getPair(address token0, address token1) internal pure returns (address, address) {
    if (token0 < token1) return (token0, token1);

    return (token1, token0);
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68-L72


However there is no check like in `sortTokens()` function in `SystemContract`. Due to lack of such checks functions that used `getPair()` can revert.

## Recommended Mitigation Steps
Consider to implement the next changes:

```diff
function getPair(address token0, address token1) internal pure returns (address, address) {
++  if (token0 == address(0)) revert InvalidAddress();
++  if (token1 == address(0)) revert InvalidAddress();
++  if (token0 == token1) revert CantBeIdenticalAddresses();
    if (token0 < token1) return (token0, token1);
    return (token1, token0);
}
```

# [NC-01] Unused lines of code.

## Description
In `pause()` function there is a check that `TSSAddress != address(0)`:

```solidity
function pause() external onlyTSS {
    if (paused) {
        revert IsPaused();
    }
    if (TSSAddress == address(0)) {
        revert ZeroAddress();
    }
    paused = true;
    emit Paused(msg.sender);
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L122-L124

Hovewer, this check is useless since there is a `onlyTSS` modifier which restrict only the `TSSAddress` to call `pause()` function and of course zero address can't do a call of this function.

## Recommended Mitigation Steps
Consider to remove an unused check:

```diff
function pause() external onlyTSS {
    if (paused) {
        revert IsPaused();
    }
--  if (TSSAddress == address(0)) {
--      revert ZeroAddress();
    }
    paused = true;
    emit Paused(msg.sender);
}
```

# [NC-02] Two instances of IZRC20 interface.

## Description
There are two instance of `IZRC20`. One of them located in `zevm/interfaces/IZRC20.sol` and the second one in `zevm/interfaces.sol`.

## Recommended Mitigation Steps
Consider to remove one file and use only the correct one.


# [NC-03] Function with `@TODO`.

## Description
There is an unfinished `hasZetaLiquidity()` function with `@TODO` mark. `@TODO` mark means that some functionality not finished yet.

```solidity
function hasZetaLiquidity() external view override returns (bool) {
    //@TODO: Implement
    return false;
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203-L206

## Recommended Mitigation Steps
Consider to implement all the functionality.

# [NC-04] Typos.

## Description
In `ERC20Custody.sol` contract there are some typo issues.

```solidity
/// @notice TSSAddress is the TSS address collectively possessed by Zeta blockchain validators. // @audit typos ? possessed => prossessed
    address public TSSAddress;
```

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L25


```solidity
// and we need to correctly process that, o we subtract an old balance from a new balance, which should be an actual received amount. // @audit typos o => so
```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L183


In `ZetaConnector.non-eth.sol` contract

```solidity
* This version is for every chain but Etherum network because in the other chains we mint and burn and in Etherum we lock and unlock // @audit typos Etherum => Ethereum
```

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L13


In `ZRC20.sol` contract:

```solidity
* @param recipient, recipiuent address to which transfer is done. // @audit recipiuent -> recipient
```

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L122


## Recommended Mitigation Steps
Consider to correct these issues.